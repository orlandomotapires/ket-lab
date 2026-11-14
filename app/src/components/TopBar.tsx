import { LOCALES, setLocale, t, useLocale, type Locale } from "../i18n";
import { useStore } from "../state/store";
import { toggleTheme, useTheme } from "../theme/theme";
import { ArrowLeftIcon, LogoMark, MoonIcon, SunIcon } from "./icons";
import { SearchBox } from "./SearchBox";

export function TopBar() {
  const theme = useTheme();
  const locale = useLocale();
  const view = useStore((s) => s.view);
  const lesson = useStore((s) => s.lesson);
  const catalog = useStore((s) => s.catalog);
  const connection = useStore((s) => s.connection);
  const backToHub = useStore((s) => s.backToHub);

  const track = lesson && catalog?.tracks.find((item) => item.id === lesson.track);

  return (
    <header className="topbar">
      <div className="topbar-left">
      {view === "lab" ? (
        <>
          <button className="btn btn-ghost btn-sm" onClick={backToHub}>
            <ArrowLeftIcon /> {t("topbar.tracks")}
          </button>
          <span className="divider" />
          <nav className="crumbs" aria-label={t("topbar.location")}>
            {lesson ? (
              <>
                <span>{track ? track.title : t("hub.track", { id: lesson.track })}</span>
                <span className="crumb-sep">/</span>
                <strong>
                  <span className="crumb-id">{lesson.id}</span>
                  {lesson.title}
                </strong>
              </>
            ) : (
              <strong>{t("topbar.sandbox")}</strong>
            )}
          </nav>
        </>
      ) : (
        <div className="brand">
          <LogoMark />
          {t("app.name")}
        </div>
      )}
      </div>
      <SearchBox />
      <div className="topbar-right">
      <span className={`status-chip is-${connection}`} role="status" title={t("topbar.engineTitle")}>
        <span className="status-dot" aria-hidden="true" />
        {t(`topbar.engine.${connection}`)}
      </span>
      <div className="segmented lang-switch" role="radiogroup" aria-label={t("topbar.language")}>
        {LOCALES.map((option) => (
          <button
            key={option.id}
            role="radio"
            aria-checked={locale === option.id}
            aria-selected={locale === option.id}
            title={option.label}
            lang={option.id}
            onClick={() => setLocale(option.id as Locale)}
          >
            {option.short}
          </button>
        ))}
      </div>
      <button
        className="btn btn-ghost btn-icon btn-sm"
        onClick={toggleTheme}
        aria-label={theme === "dark" ? t("topbar.toLight") : t("topbar.toDark")}
        title={theme === "dark" ? t("topbar.light") : t("topbar.dark")}
      >
        {theme === "dark" ? <SunIcon /> : <MoonIcon />}
      </button>
      </div>
    </header>
  );
}
