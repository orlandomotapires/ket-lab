//! Shell desktop. De propósito, ele é fino: abre a janela, inicia o motor
//! Python (sidecar) e entrega à interface a porta e o token que o motor sorteou.
//! Toda a lógica do produto vive na interface (app/) e no motor (engine/).

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc;
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager, RunEvent, State};

const STARTUP_TIMEOUT: Duration = Duration::from_secs(60);

#[derive(Clone, Serialize, Deserialize)]
struct Endpoint {
    port: u16,
    token: String,
}

struct RunningEngine {
    child: Child,
    endpoint: Endpoint,
    /// Mantido aberto enquanto o shell vive. Se o shell morrer, mesmo sem
    /// chance de limpar, o pipe fecha e o motor encerra sozinho
    /// (`--exit-on-stdin-close`).
    _stdin: ChildStdin,
}

#[derive(Default)]
struct Engine(Mutex<Option<RunningEngine>>);

impl Engine {
    /// Devolve o endereço do motor, iniciando-o (ou reiniciando-o, se caiu).
    fn endpoint(&self, app: &AppHandle) -> Result<Endpoint, String> {
        let mut slot = self.0.lock().map_err(|_| "Estado do motor corrompido.".to_string())?;
        if let Some(running) = slot.as_mut() {
            if matches!(running.child.try_wait(), Ok(None)) {
                return Ok(running.endpoint.clone());
            }
            *slot = None; // o processo terminou: inicia outro
        }
        let running = launch(app)?;
        let endpoint = running.endpoint.clone();
        *slot = Some(running);
        Ok(endpoint)
    }

    fn stop(&self) {
        if let Ok(mut slot) = self.0.lock() {
            if let Some(mut running) = slot.take() {
                let _ = running.child.kill();
                let _ = running.child.wait();
            }
        }
    }
}

/// Em desenvolvimento usa o ambiente virtual do repositório; no aplicativo
/// instalado, o executável empacotado que vai junto como recurso.
fn engine_command(app: &AppHandle) -> Result<Command, String> {
    let mut command = if cfg!(debug_assertions) {
        let engine_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("..").join("engine");
        let python = if cfg!(windows) { ".venv/Scripts/python.exe" } else { ".venv/bin/python" };
        let python = engine_dir.join(python);
        if !python.exists() {
            return Err(format!(
                "Ambiente Python ausente em {}. Rode `npm run setup`.",
                python.display()
            ));
        }
        let mut command = Command::new(python);
        command.current_dir(&engine_dir).args([
            "-m",
            "qlp_engine",
            "--allow-origin",
            "http://127.0.0.1:5173",
            "--allow-origin",
            "http://localhost:5173",
        ]);
        command
    } else {
        let name = if cfg!(windows) { "qlp-engine.exe" } else { "qlp-engine" };
        let executable = app
            .path()
            .resource_dir()
            .map_err(|error| format!("Pasta de recursos indisponível: {error}"))?
            .join("qlp-engine")
            .join(name);
        if !executable.exists() {
            return Err(format!("Motor de simulação não encontrado em {}.", executable.display()));
        }
        Command::new(executable)
    };

    command.arg("--exit-on-stdin-close");
    if let Ok(data_dir) = std::env::var("QLP_DATA_DIR") {
        command.args(["--data-dir", &data_dir]);
    }
    command.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::inherit());

    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        command.creation_flags(CREATE_NO_WINDOW);
    }
    Ok(command)
}

fn launch(app: &AppHandle) -> Result<RunningEngine, String> {
    let mut child = engine_command(app)?
        .spawn()
        .map_err(|error| format!("Não foi possível iniciar o motor de simulação: {error}"))?;
    let stdin = child.stdin.take().ok_or("Motor sem stdin.")?;
    let stdout = child.stdout.take().ok_or("Motor sem stdout.")?;

    // O motor anuncia porta e token na primeira linha do stdout.
    let (sender, receiver) = mpsc::channel::<String>();
    thread::spawn(move || {
        let mut lines = BufReader::new(stdout).lines();
        if let Some(Ok(first)) = lines.next() {
            let _ = sender.send(first);
        }
        for _ in lines {} // continua drenando para o pipe nunca encher
    });

    let announced = receiver.recv_timeout(STARTUP_TIMEOUT).map_err(|_| {
        let _ = child.kill();
        let _ = child.wait();
        "O motor de simulação não respondeu ao iniciar.".to_string()
    });
    let endpoint = announced.and_then(|line| {
        serde_json::from_str::<Endpoint>(&line)
            .map_err(|error| format!("Resposta inesperada do motor ({error}): {line}"))
    });
    match endpoint {
        Ok(endpoint) => Ok(RunningEngine { child, endpoint, _stdin: stdin }),
        Err(message) => {
            let _ = child.kill();
            let _ = child.wait();
            Err(message)
        }
    }
}

/// Escreve no stderr sem nunca entrar em pânico (o terminal pode já ter fechado).
fn log(message: &str) {
    let _ = writeln!(std::io::stderr(), "{message}");
}

/// Diagnóstico: a interface relata aqui mudanças de conexão e erros.
#[tauri::command]
fn client_log(message: String) {
    log(&format!("[interface] {message}"));
}

/// Chamado pela interface a cada (re)conexão. `async` tira a espera da thread principal.
#[tauri::command(async)]
fn engine_endpoint(app: AppHandle, engine: State<'_, Engine>) -> Result<Endpoint, String> {
    engine.endpoint(&app)
}

/// Exportação: pergunta onde salvar e grava o texto. Devolve false se o aluno cancelar.
/// A interface nunca escolhe o caminho; ele vem sempre da janela do sistema.
#[tauri::command(async)]
fn save_text_file(app: AppHandle, contents: String, file_name: String) -> Result<bool, String> {
    use tauri_plugin_dialog::DialogExt;

    let Some(path) = app
        .dialog()
        .file()
        .set_file_name(&file_name)
        .add_filter("OpenQASM", &["qasm"])
        .blocking_save_file()
    else {
        return Ok(false);
    };
    let path = path.into_path().map_err(|error| error.to_string())?;
    std::fs::write(&path, contents).map_err(|error| format!("{}: {error}", path.display()))?;
    Ok(true)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .manage(Engine::default())
        .invoke_handler(tauri::generate_handler![engine_endpoint, client_log, save_text_file])
        .setup(|app| {
            // Aquece o motor enquanto a janela carrega.
            let handle = app.handle().clone();
            thread::spawn(move || {
                if let Err(message) = handle.state::<Engine>().endpoint(&handle) {
                    log(&message);
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("falha ao iniciar o aplicativo")
        .run(|app, event| {
            if let RunEvent::Exit = event {
                app.state::<Engine>().stop();
            }
        });
}
