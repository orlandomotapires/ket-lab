import type { ReactNode, SVGProps } from "react";

function Icon({ children, size = 16, ...props }: SVGProps<SVGSVGElement> & { children: ReactNode; size?: number }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}
    >
      {children}
    </svg>
  );
}

/** Product mark: Bloch sphere with the state vector. */
export const LogoMark = ({ size = 22 }: { size?: number }) => (
  <svg className="brand-mark" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
    <circle cx="12" cy="12" r="9.25" strokeWidth="1.6" />
    <ellipse cx="12" cy="12" rx="9.25" ry="3.3" strokeWidth="1.1" opacity="0.45" />
    <path d="M12 12 17.4 6.4" strokeWidth="1.8" strokeLinecap="round" />
    <circle cx="17.6" cy="6.2" r="1.7" fill="currentColor" stroke="none" />
    <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none" />
  </svg>
);

export const InfoIcon = () => (
  <Icon>
    <circle cx="8" cy="8" r="6.25" />
    <path d="M8 7.25v4" />
    <circle cx="8" cy="4.9" r="0.55" fill="currentColor" stroke="none" />
  </Icon>
);

export const SunIcon = () => (
  <Icon>
    <circle cx="8" cy="8" r="3" />
    <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1" />
  </Icon>
);
export const MoonIcon = () => (
  <Icon>
    <path d="M13.5 9.5A5.5 5.5 0 0 1 6.5 2.5a5.5 5.5 0 1 0 7 7z" />
  </Icon>
);
export const ArrowLeftIcon = () => (
  <Icon>
    <path d="M9.5 3.5 5 8l4.5 4.5" />
  </Icon>
);
export const ChevronRightIcon = () => (
  <Icon size={14}>
    <path d="m6 3.5 4.5 4.5L6 12.5" />
  </Icon>
);
export const CheckIcon = ({ size = 16 }: { size?: number }) => (
  <Icon size={size} strokeWidth="1.9">
    <path d="m3.5 8.5 3 3 6-7" />
  </Icon>
);
export const TargetIcon = () => (
  <Icon size={14}>
    <circle cx="8" cy="8" r="6" />
    <circle cx="8" cy="8" r="2.5" />
  </Icon>
);
export const AlertIcon = () => (
  <Icon size={13} strokeWidth="1.9">
    <path d="M8 4v4.5M8 11.5v.01" />
  </Icon>
);
export const DotIcon = () => (
  <svg width="6" height="6" viewBox="0 0 6 6" aria-hidden="true">
    <circle cx="3" cy="3" r="3" fill="currentColor" />
  </svg>
);
export const FirstIcon = () => (
  <Icon>
    <path d="M4 3.5v9M12 3.5 7 8l5 4.5" />
  </Icon>
);
export const PrevIcon = () => (
  <Icon>
    <path d="M10 3.5 5.5 8l4.5 4.5" />
  </Icon>
);
export const NextIcon = () => (
  <Icon>
    <path d="m6 3.5 4.5 4.5L6 12.5" />
  </Icon>
);
export const LastIcon = () => (
  <Icon>
    <path d="M12 3.5v9M4 3.5 9 8l-5 4.5" />
  </Icon>
);
export const ExportIcon = () => (
  <Icon>
    <path d="M8 2v8M5 7l3 3 3-3M3 11.5v1A1.5 1.5 0 0 0 4.5 14h7a1.5 1.5 0 0 0 1.5-1.5v-1" />
  </Icon>
);
export const BookIcon = () => (
  <Icon>
    <path d="M3 3.5A1.5 1.5 0 0 1 4.5 2H13v10H4.5A1.5 1.5 0 0 0 3 13.5zM3 13.5A1.5 1.5 0 0 0 4.5 15H13v-3" />
  </Icon>
);
export const ImportIcon = () => (
  <Icon>
    <path d="M8 10V2M5 5l3-3 3 3M3 11.5v1A1.5 1.5 0 0 0 4.5 14h7a1.5 1.5 0 0 0 1.5-1.5v-1" />
  </Icon>
);

export const GlossaryIcon = () => (
  <Icon>
    <path d="M2.5 13 6 3l3.5 10M3.8 9.5h4.4" />
    <path d="M11 6.5h3M11 9.5h3M11 12.5h3" />
  </Icon>
);

export const NoteIcon = () => (
  <Icon>
    <path d="M3.5 2.5h9v11h-9z" />
    <path d="M5.5 5.5h5M5.5 8h5M5.5 10.5h3" />
  </Icon>
);
