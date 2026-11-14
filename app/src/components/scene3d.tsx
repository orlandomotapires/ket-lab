/**
 * Cenas 3D: esferas de Bloch e Q-Sphere. Ficam num módulo separado, carregado
 * sob demanda, porque o Three.js é a parte mais pesada da interface.
 */
import { Html } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import * as THREE from "three";
import type { Complex, Vec3 } from "../engine/types";
import { t } from "../strings";
import { phaseColor, phaseOf, probability, qspherePositions } from "../lib/quantum";
import { PALETTES, useTheme, type Palette } from "../theme/theme";

const CELL = 2.9; // largura de cada esfera na grade, em unidades da cena
const ANIMATION_S = 0.45;
const UP = new THREE.Vector3(0, 1, 0);

/** Bloch (x, y, z) -> cena (y, z, x): Z para cima, X em direção ao observador. */
function toScene([x, y, z]: Vec3, out = new THREE.Vector3()): THREE.Vector3 {
  return out.set(y, z, x);
}

function circleGeometry(plane: "xy" | "xz" | "yz"): THREE.BufferGeometry {
  const points: THREE.Vector3[] = [];
  for (let i = 0; i < 96; i++) {
    const a = (i / 96) * Math.PI * 2;
    const c = Math.cos(a);
    const s = Math.sin(a);
    points.push(plane === "xy" ? new THREE.Vector3(c, s, 0) : plane === "xz" ? new THREE.Vector3(c, 0, s) : new THREE.Vector3(0, c, s));
  }
  return new THREE.BufferGeometry().setFromPoints(points);
}

const CIRCLE_XY = circleGeometry("xy");
const CIRCLE_XZ = circleGeometry("xz");
const CIRCLE_YZ = circleGeometry("yz");
const AXES = new THREE.BufferGeometry().setFromPoints([
  new THREE.Vector3(-1, 0, 0), new THREE.Vector3(1, 0, 0),
  new THREE.Vector3(0, -1, 0), new THREE.Vector3(0, 1, 0),
  new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 0, 1),
]);

const scratchQ = new THREE.Quaternion();
const scratchA = new THREE.Vector3();
const scratchB = new THREE.Vector3();
const IDENTITY = new THREE.Quaternion();

/** Interpola girando sobre a esfera (e não cortando pelo centro, o que pareceria um estado misto). */
function interpolate(from: THREE.Vector3, to: THREE.Vector3, s: number, axis: THREE.Vector3 | null, out: THREE.Vector3) {
  const lengthFrom = from.length();
  const lengthTo = to.length();
  if (lengthFrom < 1e-3 || lengthTo < 1e-3) return out.lerpVectors(from, to, s);
  const a = scratchA.copy(from).divideScalar(lengthFrom);
  const b = scratchB.copy(to).divideScalar(lengthTo);
  if (a.dot(b) < -0.9995) {
    // Antípodas: o caminho é ambíguo; usa o eixo da porta quando ele serve.
    let rotation = axis && Math.abs(axis.dot(a)) < 1e-3 ? axis : null;
    if (!rotation) {
      rotation = new THREE.Vector3(1, 0, 0).cross(a);
      if (rotation.lengthSq() < 1e-6) rotation = new THREE.Vector3(0, 0, 1).cross(a);
      rotation.normalize();
    }
    scratchQ.setFromAxisAngle(rotation, Math.PI * s);
  } else {
    scratchQ.setFromUnitVectors(a, b);
    scratchQ.copy(IDENTITY.clone().slerp(scratchQ, s));
  }
  return out.copy(a).applyQuaternion(scratchQ).multiplyScalar(lengthFrom + (lengthTo - lengthFrom) * s);
}

// --------------------------------------------------------------------------- //
// Peças comuns
// --------------------------------------------------------------------------- //

interface View {
  yaw: number;
  pitch: number;
}

/** Contêiner com canvas, câmera ortográfica e rotação por arraste. */
function SceneFrame({ cols, rows, children }: { cols: number; rows: number; children: (view: View) => ReactNode }) {
  const [view, setView] = useState<View>({ yaw: -0.6, pitch: 0.32 });
  const drag = useRef<{ x: number; y: number } | null>(null);

  const onPointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    drag.current = { x: event.clientX, y: event.clientY };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const onPointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!drag.current) return;
    const dx = event.clientX - drag.current.x;
    const dy = event.clientY - drag.current.y;
    drag.current = { x: event.clientX, y: event.clientY };
    setView((v) => ({ yaw: v.yaw + dx * 0.01, pitch: Math.max(-1.4, Math.min(1.4, v.pitch + dy * 0.01)) }));
  };
  const onPointerUp = () => {
    drag.current = null;
  };

  return (
    <div
      className="scene"
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      title={t("viz.dragToRotate")}
    >
      <Canvas orthographic frameloop="demand" dpr={[1, 2]} camera={{ position: [0, 0, 10], near: 0.1, far: 50, zoom: 80 }} gl={{ antialias: true, alpha: true }}>
        <FitCamera cols={cols} rows={rows} />
        {children(view)}
      </Canvas>
    </div>
  );
}

function FitCamera({ cols, rows }: { cols: number; rows: number }) {
  const { camera, size, invalidate } = useThree();
  useEffect(() => {
    // Deixa espaço para a legenda no topo e no rodapé do palco.
    camera.zoom = Math.min(size.width / (cols * CELL), (size.height - 40) / (rows * CELL));
    camera.position.y = -6 / camera.zoom;
    camera.updateProjectionMatrix();
    invalidate();
  }, [camera, size, cols, rows, invalidate]);
  return null;
}

function WireSphere({ palette, showAxes = true }: { palette: Palette; showAxes?: boolean }) {
  return (
    <>
      <mesh>
        <sphereGeometry args={[1, 48, 32]} />
        <meshBasicMaterial color={palette.sphere} transparent opacity={0.06} depthWrite={false} />
      </mesh>
      <lineLoop geometry={CIRCLE_XZ}>
        <lineBasicMaterial color={palette.lineStrong} />
      </lineLoop>
      <lineLoop geometry={CIRCLE_XY}>
        <lineBasicMaterial color={palette.line} />
      </lineLoop>
      <lineLoop geometry={CIRCLE_YZ}>
        <lineBasicMaterial color={palette.line} />
      </lineLoop>
      {showAxes && (
        <lineSegments geometry={AXES}>
          <lineBasicMaterial color={palette.line} />
        </lineSegments>
      )}
    </>
  );
}

/** Contorno fixo (não gira com o arraste), para a esfera manter a silhueta. */
function Outline({ palette }: { palette: Palette }) {
  return (
    <lineLoop geometry={CIRCLE_XY}>
      <lineBasicMaterial color={palette.lineStrong} />
    </lineLoop>
  );
}

function Label({ position, children, className = "" }: { position: [number, number, number]; children: ReactNode; className?: string }) {
  return (
    <Html position={position} center className={`scene-label ${className}`} zIndexRange={[1, 0]}>
      {children}
    </Html>
  );
}

function grid(count: number): { cols: number; rows: number } {
  const cols = count <= 3 ? count : Math.ceil(Math.sqrt(count));
  return { cols, rows: Math.ceil(count / cols) };
}

// --------------------------------------------------------------------------- //
// Esferas de Bloch
// --------------------------------------------------------------------------- //

function StateArrow({ target, axis, palette, dark, animate }: {
  target: Vec3; axis: Vec3 | null; palette: Palette; dark: boolean; animate: boolean;
}) {
  const arrow = useRef<THREE.Group>(null!);
  const shaft = useRef<THREE.Mesh>(null!);
  const dot = useRef<THREE.Mesh>(null!);
  const material = useMemo(() => new THREE.MeshBasicMaterial(), []);
  const invalidate = useThree((s) => s.invalidate);
  const motion = useRef({
    from: toScene(target), to: toScene(target), current: toScene(target), axis: null as THREE.Vector3 | null, t: 1,
  });

  useEffect(() => {
    const m = motion.current;
    m.from.copy(m.current);
    toScene(target, m.to);
    m.axis = axis ? toScene(axis) : null;
    m.t = animate ? 0 : 1;
    if (!animate) m.current.copy(m.to);
    invalidate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target[0], target[1], target[2]]);

  useEffect(() => invalidate(), [palette, invalidate]);

  useFrame((_, delta) => {
    const m = motion.current;
    if (m.t < 1) {
      m.t = Math.min(1, m.t + Math.min(delta, 1 / 30) / ANIMATION_S);
      const eased = m.t < 0.5 ? 2 * m.t * m.t : 1 - (-2 * m.t + 2) ** 2 / 2;
      interpolate(m.from, m.to, eased, m.axis, m.current);
      invalidate();
    }
    const length = m.current.length();
    const visible = length > 0.04;
    arrow.current.visible = visible;
    dot.current.visible = !visible;
    if (visible) {
      arrow.current.quaternion.setFromUnitVectors(UP, scratchA.copy(m.current).divideScalar(length));
      shaft.current.scale.y = Math.max(length - 0.16, 0.001);
      shaft.current.position.y = Math.max(length - 0.16, 0.001) / 2;
      arrow.current.children[1].position.y = Math.max(length - 0.08, 0.08);
    }
    // Fase relativa = ângulo em torno do eixo Z de Bloch (cena: plano z-x).
    const equatorial = Math.hypot(m.current.z, m.current.x);
    material.color.setStyle(equatorial > 0.05 ? phaseColor(Math.atan2(m.current.x, m.current.z), dark) : palette.accent);
  });

  return (
    <>
      <group ref={arrow}>
        <mesh ref={shaft} material={material}>
          <cylinderGeometry args={[0.024, 0.024, 1, 12]} />
        </mesh>
        <mesh material={material}>
          <coneGeometry args={[0.075, 0.17, 24]} />
        </mesh>
      </group>
      <mesh ref={dot} material={material} visible={false}>
        <sphereGeometry args={[0.06, 16, 12]} />
      </mesh>
    </>
  );
}

export function BlochScene({ vectors, axes, labels }: { vectors: Vec3[]; axes: (Vec3 | null)[]; labels?: string[] }) {
  const theme = useTheme();
  const palette = PALETTES[theme];
  const reducedMotion = useMemo(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches, []);
  const { cols, rows } = grid(vectors.length);

  return (
    <SceneFrame cols={cols} rows={rows}>
      {(view) =>
        vectors.map((vector, index) => {
          const col = index % cols;
          const row = Math.floor(index / cols);
          const label = labels?.[index] ?? (vectors.length > 1 ? `q${index}` : null);
          return (
            <group key={index} position={[(col - (cols - 1) / 2) * CELL, ((rows - 1) / 2 - row) * CELL, 0]}>
              <Outline palette={palette} />
              {label && <Label position={[0, -1.3, 0]} className="is-caption">{label}</Label>}
              <group rotation={[view.pitch, view.yaw, 0]}>
                <WireSphere palette={palette} />
                <Label position={[0, 1.17, 0]}>|0⟩</Label>
                <Label position={[0, -1.17, 0]}>|1⟩</Label>
                <Label position={[0, 0, 1.15]} className="is-axis">x</Label>
                <Label position={[1.15, 0, 0]} className="is-axis">y</Label>
                <StateArrow target={vector} axis={axes[index] ?? null} palette={palette} dark={theme === "dark"} animate={!reducedMotion} />
              </group>
            </group>
          );
        })
      }
    </SceneFrame>
  );
}

// --------------------------------------------------------------------------- //
// Q-Sphere
// --------------------------------------------------------------------------- //

const MIN_PROBABILITY = 1e-6;

function QSphereNodes({ amplitudes, numQubits, palette, dark }: {
  amplitudes: Complex[]; numQubits: number; palette: Palette; dark: boolean;
}) {
  const positions = useMemo(() => qspherePositions(numQubits), [numQubits]);
  const invalidate = useThree((s) => s.invalidate);
  useEffect(() => invalidate(), [amplitudes, palette, invalidate]);
  const showEmpty = amplitudes.length <= 16;

  return (
    <>
      {amplitudes.map((amplitude, index) => {
        const p = probability(amplitude);
        const [x, y, z] = positions[index];
        const bits = index.toString(2).padStart(numQubits, "0");
        if (p < MIN_PROBABILITY) {
          return showEmpty ? (
            <mesh key={index} position={[x, y, z]}>
              <sphereGeometry args={[0.022, 10, 8]} />
              <meshBasicMaterial color={palette.lineStrong} />
            </mesh>
          ) : null;
        }
        const color = phaseColor(phaseOf(amplitude), dark);
        const radius = 0.05 + 0.13 * Math.sqrt(p);
        const line = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(x, y, z)]);
        return (
          <group key={index}>
            <lineSegments geometry={line}>
              <lineBasicMaterial color={color} transparent opacity={0.55} />
            </lineSegments>
            <mesh position={[x, y, z]}>
              <sphereGeometry args={[radius, 24, 16]} />
              <meshBasicMaterial color={color} />
            </mesh>
            <Label position={labelPosition([x, y, z], radius)}>|{bits}⟩</Label>
          </group>
        );
      })}
    </>
  );
}

/** Rótulo afastado do ponto: nos polos vai para cima/baixo, no resto, para fora. */
function labelPosition([x, y, z]: Vec3, radius: number): [number, number, number] {
  if (Math.abs(y) > 0.95) return [0, y + Math.sign(y) * (radius + 0.16), 0];
  const out = 1 + radius + 0.2;
  return [x * out, y * out, z * out];
}

export function QSphereScene({ amplitudes, numQubits }: { amplitudes: Complex[]; numQubits: number }) {
  const theme = useTheme();
  const palette = PALETTES[theme];
  return (
    <SceneFrame cols={1} rows={1}>
      {(view) => (
        <>
          <Outline palette={palette} />
          <group rotation={[view.pitch, view.yaw, 0]}>
            <WireSphere palette={palette} showAxes={false} />
            <QSphereNodes amplitudes={amplitudes} numQubits={numQubits} palette={palette} dark={theme === "dark"} />
          </group>
        </>
      )}
    </SceneFrame>
  );
}
