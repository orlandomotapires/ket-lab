import { useRef, type KeyboardEvent, type PointerEvent } from "react";

/** A drag handle between two panels. `value` is the first panel's share of `container`, in percent,
 *  kept between `min` and `max`. Arrow keys move it too. Double-click goes back to `initial`. */
export function Splitter({ orientation, value, min, max, initial, onChange, label, container, className = "" }: {
  orientation: "vertical" | "horizontal";
  value: number;
  min: number;
  max: number;
  initial: number;
  onChange: (value: number) => void;
  label: string;
  container: () => HTMLElement | null;
  className?: string;
}) {
  const drag = useRef<{ start: number; value: number; size: number } | null>(null);
  const vertical = orientation === "vertical";
  const clamp = (next: number) => Math.min(max, Math.max(min, next));

  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    const box = container()?.getBoundingClientRect();
    if (!box || event.button !== 0) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { start: vertical ? event.clientX : event.clientY, value, size: vertical ? box.width : box.height };
    document.body.classList.add(vertical ? "is-resizing-x" : "is-resizing-y");
  };
  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const d = drag.current;
    if (!d || d.size <= 0) return;
    const moved = (vertical ? event.clientX : event.clientY) - d.start;
    onChange(clamp(d.value + (moved / d.size) * 100));
  };
  const onPointerUp = () => {
    drag.current = null;
    document.body.classList.remove("is-resizing-x", "is-resizing-y");
  };
  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const step = event.shiftKey ? 10 : 2;
    const back = vertical ? "ArrowLeft" : "ArrowUp";
    const forward = vertical ? "ArrowRight" : "ArrowDown";
    const next =
      event.key === back ? value - step
      : event.key === forward ? value + step
      : event.key === "Home" ? min
      : event.key === "End" ? max
      : null;
    if (next === null) return;
    event.preventDefault();
    onChange(clamp(next));
  };

  return (
    <div
      className={`splitter is-${orientation} ${className}`}
      role="separator"
      aria-orientation={vertical ? "vertical" : "horizontal"}
      aria-label={label}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={Math.round(value)}
      tabIndex={0}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onLostPointerCapture={onPointerUp}
      onDoubleClick={() => onChange(initial)}
      onKeyDown={onKeyDown}
    />
  );
}
