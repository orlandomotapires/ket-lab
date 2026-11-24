/**
 * 3D scenes: Bloch spheres and Q-Sphere. They live in a separate module, loaded
 * on demand, because Three.js is the heaviest part of the interface.
 */
import { Html } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Component, useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import * as THREE from "three";
import type { Complex, Vec3 } from "../engine/types";
import { t } from "../strings";
import { ZoomInIcon, ZoomOutIcon } from "./icons";
import { blochTerms, phaseColor, phaseOf, probability, qspherePositions } from "../lib/quantum";
import { PALETTES, useTheme, type Palette } from "../theme/theme";

const CELL = 2.9; // width of each sphere in the grid, in scene units
const ANIMATION_S = 0.45;
const UP = new THREE.Vector3(0, 1, 0);

/** Bloch (x, y, z) -> scene (y, z, x): Z up, X toward the viewer. */
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

/** Interpolates by rotating over the sphere (not cutting through the center, which would look like a mixed state). */
function interpolate(from: THREE.Vector3, to: THREE.Vector3, s: number, axis: THREE.Vector3 | null, out: THREE.Vector3) {
  const lengthFrom = from.length();
  const lengthTo = to.length();
  if (lengthFrom < 1e-3 || lengthTo < 1e-3) return out.lerpVectors(from, to, s);
  const a = scratchA.copy(from).divideScalar(lengthFrom);
  const b = scratchB.copy(to).divideScalar(lengthTo);
  if (a.dot(b) < -0.9995) {
    // Antipodes: the path is ambiguous; uses the gate axis when it fits.
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
// Common pieces
// --------------------------------------------------------------------------- //

interface View {
  yaw: number;
  pitch: number;
}

/** Zoom of a scene: a factor over the fitted size, and where the camera looks (scene units). */
interface Zoom {
  factor: number;
  x: number;
  y: number;
}

const FIT: Zoom = { factor: 1, x: 0, y: 0 };
const MIN_ZOOM = 1;
const MAX_ZOOM = 8;
const ZOOM_STEP = 1.4;

/** Pixels per scene unit when the whole grid fits, leaving room for the captions above and below. */
function fitScale(width: number, height: number, cols: number, rows: number): number {
  return Math.min(width / (cols * CELL), (height - 40) / (rows * CELL));
}

/** Zooms to `factor`, keeping the scene point under (px, py) (pixels from the frame's top left) where it is. */
function zoomAt(zoom: Zoom, factor: number, px: number, py: number, width: number, height: number, base: number): Zoom {
  const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, factor));
  if (next === MIN_ZOOM) return FIT;
  const dx = px - width / 2;
  const dy = height / 2 - py;
  const before = base * zoom.factor;
  const after = base * next;
  // The point under the pointer: camera + offset / scale. It stays put when the scale changes.
  return { factor: next, x: zoom.x + dx / before - dx / after, y: zoom.y + dy / before - dy / after };
}

/** Container with canvas, orthographic camera, drag rotation and zoom: pinch, Ctrl/⌘ + wheel
 *  (a trackpad pinch arrives as one) or the buttons. A plain wheel still scrolls the panel. */
let webgl2: boolean | null = null;
/** Three.js needs WebGL 2. Some browsers turn it off (no GPU, policy, privacy settings). */
function hasWebGL2(): boolean {
  if (webgl2 === null) {
    try {
      const gl = document.createElement("canvas").getContext("webgl2");
      webgl2 = gl !== null;
      gl?.getExtension("WEBGL_lose_context")?.loseContext();
    } catch {
      webgl2 = false;
    }
  }
  return webgl2;
}

function NoWebGL() {
  return <div className="scene scene-unavailable" role="note">{t("viz.noWebgl")}</div>;
}

/** A WebGL failure the check above missed (context lost, driver error) costs the 3D view, not the page. */
class WebGLBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? <NoWebGL /> : this.props.children;
  }
}

function SceneFrame(props: { cols: number; rows: number; children: (view: View) => ReactNode }) {
  if (!hasWebGL2()) return <NoWebGL />;
  return (
    <WebGLBoundary>
      <InteractiveScene {...props} />
    </WebGLBoundary>
  );
}

function InteractiveScene({ cols, rows, children }: { cols: number; rows: number; children: (view: View) => ReactNode }) {
  const [view, setView] = useState<View>({ yaw: -0.6, pitch: 0.32 });
  const [zoom, setZoom] = useState<Zoom>(FIT);
  const frameRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number } | null>(null);
  // Touch points on the scene: two of them pinch.
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const pinch = useRef<number | null>(null);

  const zoomBy = (ratio: number, clientX?: number, clientY?: number) => {
    const rect = frameRef.current?.getBoundingClientRect();
    if (!rect) return;
    const px = clientX === undefined ? rect.width / 2 : clientX - rect.left;
    const py = clientY === undefined ? rect.height / 2 : clientY - rect.top;
    const base = fitScale(rect.width, rect.height, cols, rows);
    setZoom((z) => zoomAt(z, z.factor * ratio, px, py, rect.width, rect.height, base));
  };

  // React wheel listeners are passive, and Ctrl + wheel must not zoom the whole page.
  useEffect(() => {
    const el = frameRef.current;
    if (!el) return;
    const onWheel = (event: WheelEvent) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      // A mouse notch (deltaY about 100) zooms by about 1.35; a trackpad pinch sends many small deltas.
      const delta = Math.max(-50, Math.min(50, event.deltaY));
      zoomBy(Math.exp(-delta * 0.006), event.clientX, event.clientY);
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  });

  const onPointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    event.currentTarget.setPointerCapture(event.pointerId);
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      pinch.current = Math.hypot(a.x - b.x, a.y - b.y);
      drag.current = null;
    } else {
      drag.current = { x: event.clientX, y: event.clientY };
    }
  };
  const onPointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (pointers.current.has(event.pointerId)) pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pinch.current !== null && pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      const distance = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch.current > 0) zoomBy(distance / pinch.current, (a.x + b.x) / 2, (a.y + b.y) / 2);
      pinch.current = distance;
      return;
    }
    if (!drag.current) return;
    const dx = event.clientX - drag.current.x;
    const dy = event.clientY - drag.current.y;
    drag.current = { x: event.clientX, y: event.clientY };
    setView((v) => ({ yaw: v.yaw + dx * 0.01, pitch: Math.max(-1.4, Math.min(1.4, v.pitch + dy * 0.01)) }));
  };
  const onPointerUp = (event: ReactPointerEvent<HTMLDivElement>) => {
    pointers.current.delete(event.pointerId);
    if (pointers.current.size < 2) pinch.current = null;
    drag.current = null;
  };

  const zoomed = zoom.factor > MIN_ZOOM;
  return (
    <>
      <div
        ref={frameRef}
        className="scene"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        onDoubleClick={() => setZoom(FIT)}
        title={t("viz.dragToRotate")}
      >
        <Canvas orthographic frameloop="demand" dpr={[1, 2]} camera={{ position: [0, 0, 10], near: 0.1, far: 50, zoom: 80 }} gl={{ antialias: true, alpha: true }}>
          <FitCamera cols={cols} rows={rows} zoom={zoom} />
          {children(view)}
        </Canvas>
      </div>
      <div className="scene-zoom" role="group" aria-label={t("viz.zoom")}>
        <button type="button" onClick={() => zoomBy(1 / ZOOM_STEP)} disabled={!zoomed} aria-label={t("viz.zoomOut")} title={t("viz.zoomOut")}>
          <ZoomOutIcon />
        </button>
        <button type="button" onClick={() => zoomBy(ZOOM_STEP)} disabled={zoom.factor >= MAX_ZOOM} aria-label={t("viz.zoomIn")} title={t("viz.zoomIn")}>
          <ZoomInIcon />
        </button>
        {zoomed && (
          <button type="button" className="scene-zoom-reset" onClick={() => setZoom(FIT)} title={t("viz.zoomResetHint")}>
            {t("viz.zoomReset")}
          </button>
        )}
      </div>
    </>
  );
}

function FitCamera({ cols, rows, zoom }: { cols: number; rows: number; zoom: Zoom }) {
  const { camera, size, invalidate } = useThree();
  useEffect(() => {
    const base = fitScale(size.width, size.height, cols, rows);
    camera.zoom = base * zoom.factor;
    // -6 / base leaves room for the caption at the top of the stage. It is the same shift at every
    // zoom, so zooming about the pointer (zoomAt) is not thrown off by it.
    camera.position.x = zoom.x;
    camera.position.y = zoom.y - 6 / base;
    camera.updateProjectionMatrix();
    invalidate();
  }, [camera, size, cols, rows, zoom, invalidate]);
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

/** Fixed outline (does not rotate with the drag), so the sphere keeps its silhouette. */
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
// Bloch spheres
// --------------------------------------------------------------------------- //

/** The state at the arrow's tip, as the combination α|0⟩ + β|1⟩ (or "mixed" when there is none). */
function StateEquation({ target, named }: { target: Vec3; named: boolean }) {
  const terms = blochTerms(target);
  if (!terms) return <span className="is-mixed">{t("viz.tipMixed")}</span>;
  const { zero, sign, factor, phase, one } = terms;
  // With several spheres, a basis state would only repeat the pole's own label.
  if (!named && (zero === null || one === null)) return null;
  return (
    <span className="state-equation-text">
      {named && "|ψ⟩ = "}
      {zero !== null && <>{zero}|0⟩</>}
      {one !== null && (
        <>
          {zero !== null ? ` ${sign} ` : sign === "−" ? "−" : ""}
          {one}
          {factor}
          {phase && <>e<sup>i{phase}</sup></>}
          |1⟩
        </>
      )}
    </span>
  );
}

function StateArrow({ target, axis, palette, dark, animate, named }: {
  target: Vec3; axis: Vec3 | null; palette: Palette; dark: boolean; animate: boolean; named: boolean;
}) {
  const arrow = useRef<THREE.Group>(null!);
  const tip = useRef<THREE.Group>(null!);
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
    tip.current.position.copy(m.current).multiplyScalar(length > 0.04 ? (length + 0.1) / length : 1);
    arrow.current.visible = visible;
    dot.current.visible = !visible;
    if (visible) {
      arrow.current.quaternion.setFromUnitVectors(UP, scratchA.copy(m.current).divideScalar(length));
      shaft.current.scale.y = Math.max(length - 0.16, 0.001);
      shaft.current.position.y = Math.max(length - 0.16, 0.001) / 2;
      arrow.current.children[1].position.y = Math.max(length - 0.08, 0.08);
    }
    // Relative phase = angle around the Bloch Z axis (scene: z-x plane).
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
      <group ref={tip}>
        <Html className="scene-label state-equation" zIndexRange={[2, 1]}>
          <StateEquation target={target} named={named} />
        </Html>
      </group>
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
                <StateArrow target={vector} axis={axes[index] ?? null} palette={palette} dark={theme === "dark"} animate={!reducedMotion} named={vectors.length === 1} />
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

/** Label offset from the point: at the poles it goes up/down, elsewhere, outward. */
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
