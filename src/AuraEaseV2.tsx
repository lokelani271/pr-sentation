import {
	AbsoluteFill,
	Img,
	interpolate,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';
import {
	TransitionSeries,
	springTiming,
	linearTiming,
} from '@remotion/transitions';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {fade} from '@remotion/transitions/fade';

// ── Brand ───────────────────────────────────────────────────────────────────
const NAVY  = '#1B2A4A';
const GOLD  = '#C59E50';
const WHITE = '#FFFFFF';
const ICE   = '#A8D8EA';
const FIRE  = '#FF6B35';
const FONT  = '"Helvetica Neue", Arial, sans-serif';

// ── Helpers ──────────────────────────────────────────────────────────────────
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

function slamSpring(frame: number, fps: number, delay = 0) {
	const f = frame - delay;
	return spring({fps, frame: f, config: {damping: 40, stiffness: 380, mass: 0.6}});
}

function slamStyle(frame: number, fps: number, delay = 0) {
	const p = slamSpring(frame, fps, delay);
	return {
		transform:  `scale(${interpolate(p, [0, 1], [2.6, 1])})`,
		opacity:    interpolate(frame - delay, [0, 4], [0, 1], clamp),
		display:    'inline-block' as const,
	};
}

// Optional AI background — renders only when the file exists in public/bg/
function BgImage({src, overlay = 0.55}: {src: string; overlay?: number}) {
	return (
		<AbsoluteFill>
			<Img
				src={staticFile(src)}
				style={{width: '100%', height: '100%', objectFit: 'cover'}}
			/>
			<AbsoluteFill
				style={{background: `rgba(${overlay < 0.5 ? '0,0,0' : '27,42,74'},${overlay})`}}
			/>
		</AbsoluteFill>
	);
}

// ── Scene 1 — HOOK (70f = 2.3s) ─────────────────────────────────────────────
// "HATE BACK PAIN?" — word-by-word slam + glowing underline
const Scene1: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const bgGlow = interpolate(Math.sin((frame / 20) * Math.PI), [-1, 1], [0, 0.12]);
	const lineW  = interpolate(frame, [30, 52], [0, 70], clamp);
	const subOp  = interpolate(frame, [44, 60], [0, 1], clamp);

	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(circle at 50% 46%, rgba(197,158,80,${bgGlow}) 0%, ${NAVY} 55%)`,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
			}}
		>
			{/* Try AI background if generated */}
			<BgImage src="bg/bg_gym.jpg" overlay={0.7} />

			<div style={{textAlign: 'center', position: 'relative', zIndex: 1}}>
				{/* Word-by-word slam */}
				{[
					{word: 'HATE',  color: WHITE, delay: 0},
					{word: 'BACK',  color: GOLD,  delay: 8},
					{word: 'PAIN?', color: WHITE, delay: 16},
				].map(({word, color, delay}) => (
					<div key={word} style={{...slamStyle(frame, fps, delay), color, fontSize: 155, fontFamily: FONT, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2}}>
						{word}
					</div>
				))}

				{/* Animated gold underline */}
				<div style={{
					width: `${lineW}%`,
					height: 5,
					background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
					margin: '18px auto 0',
					borderRadius: 3,
				}} />

				{/* Subtitle */}
				<div style={{
					opacity: subOp,
					fontSize: 46,
					fontFamily: FONT,
					fontWeight: 400,
					color: 'rgba(255,255,255,0.75)',
					marginTop: 28,
					letterSpacing: 3,
				}}>
					You're not alone.
				</div>
			</div>
		</AbsoluteFill>
	);
};

// ── Scene 2 — PROBLEM (80f = 2.7s) ──────────────────────────────────────────
// 3 old solutions, each getting crossed out → "There's a better way"
const ITEMS = [
	{emoji: '💊', label: 'PILLS',       delay: 0},
	{emoji: '🧊', label: 'ICE BATHS',   delay: 22},
	{emoji: '💉', label: 'INJECTIONS',  delay: 44},
];

const Scene2: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const endOp = interpolate(frame, [62, 76], [0, 1], clamp);

	return (
		<AbsoluteFill
			style={{
				background: NAVY,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				gap: 52,
				padding: '0 80px',
			}}
		>
			<div style={{
				fontSize: 58,
				fontFamily: FONT,
				fontWeight: 300,
				color: 'rgba(255,255,255,0.6)',
				letterSpacing: 2,
				marginBottom: 12,
			}}>
				Tried everything?
			</div>

			{ITEMS.map(({emoji, label, delay}) => {
				const localFrame = frame - delay;
				const slideP = spring({fps, frame: localFrame, config: {damping: 70, stiffness: 160}});
				const x      = interpolate(slideP, [0, 1], [160, 0]);
				const itemOp = interpolate(localFrame, [0, 6], [0, 1], clamp);
				const strikeW = interpolate(localFrame - 14, [0, 14], [0, 100], clamp);

				return (
					<div key={label} style={{
						transform: `translateX(${x}px)`,
						opacity: itemOp,
						position: 'relative',
						display: 'flex',
						alignItems: 'center',
						gap: 28,
						width: '100%',
					}}>
						<span style={{fontSize: 64}}>{emoji}</span>
						<span style={{
							fontSize: 64,
							fontFamily: FONT,
							fontWeight: 800,
							color: 'rgba(255,255,255,0.85)',
						}}>
							{label}
						</span>

						{/* Strikethrough */}
						<div style={{
							position: 'absolute',
							left: 88,
							top: '50%',
							height: 5,
							width: `${strikeW}%`,
							maxWidth: 480,
							background: '#FF4444',
							borderRadius: 3,
							transformOrigin: 'left center',
						}} />
					</div>
				);
			})}

			<div style={{
				opacity: endOp,
				fontSize: 52,
				fontFamily: FONT,
				fontWeight: 500,
				color: GOLD,
				letterSpacing: 2,
				marginTop: 8,
			}}>
				There's a better way ↓
			</div>
		</AbsoluteFill>
	);
};

// ── Scene 3 — PRODUCT (130f = 4.3s) ─────────────────────────────────────────
// HOT | COLD split reveal + AuraEase product card + benefits
const Scene3: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	// Split reveal: each half expands from center outward
	const splitP   = spring({fps, frame, config: {damping: 60, stiffness: 140}});
	const splitW   = interpolate(splitP, [0, 1], [0, 50]); // % of screen width each side

	// Product card drops in
	const cardP    = spring({fps, frame: frame - 20, config: {damping: 70, stiffness: 120}});
	const cardY    = interpolate(cardP, [0, 1], [-350, 0]);
	const cardOp   = interpolate(frame, [20, 36], [0, 1], clamp);

	// Text cascade
	const t1Op = interpolate(frame, [55, 72], [0, 1], clamp);
	const t2Op = interpolate(frame, [72, 88], [0, 1], clamp);
	const t3Op = interpolate(frame, [88, 105], [0, 1], clamp);

	// Subtle glow pulse on product
	const glow = interpolate(Math.sin((frame / 18) * Math.PI), [-1, 1], [0.15, 0.35]);

	return (
		<AbsoluteFill style={{background: NAVY, overflow: 'hidden'}}>

			{/* HOT half — left */}
			<div style={{
				position: 'absolute',
				left: 0, top: 0,
				width: `${splitW}%`,
				height: '100%',
				background: 'linear-gradient(160deg, #6B1E00 0%, #C94B1A 35%, #FF6B35 70%, #FFA559 100%)',
			}} />

			{/* COLD half — right */}
			<div style={{
				position: 'absolute',
				right: 0, top: 0,
				width: `${splitW}%`,
				height: '100%',
				background: 'linear-gradient(200deg, #0D2137 0%, #1A4A6B 35%, #2E7AA6 70%, #A8D8EA 100%)',
			}} />

			{/* Center divider glow */}
			{splitW > 5 && (
				<div style={{
					position: 'absolute',
					left: '50%',
					top: 0,
					width: 3,
					height: '100%',
					background: `linear-gradient(180deg, transparent 5%, rgba(255,255,255,0.6) 30%, rgba(255,255,255,0.9) 50%, rgba(255,255,255,0.6) 70%, transparent 95%)`,
					transform: 'translateX(-50%)',
					boxShadow: '0 0 20px rgba(255,255,255,0.4)',
				}} />
			)}

			{/* HOT / COLD labels */}
			<div style={{
				position: 'absolute',
				top: '14%',
				left: 0,
				width: '50%',
				opacity: t1Op,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				gap: 8,
			}}>
				<div style={{fontSize: 90}}>🔥</div>
				<div style={{fontSize: 52, fontFamily: FONT, fontWeight: 900, color: WHITE, letterSpacing: 4}}>HOT</div>
			</div>

			<div style={{
				position: 'absolute',
				top: '14%',
				right: 0,
				width: '50%',
				opacity: t1Op,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				gap: 8,
			}}>
				<div style={{fontSize: 90}}>❄️</div>
				<div style={{fontSize: 52, fontFamily: FONT, fontWeight: 900, color: WHITE, letterSpacing: 4}}>COLD</div>
			</div>

			{/* Product card — center */}
			<div style={{
				position: 'absolute',
				top: '38%',
				left: '50%',
				transform: `translate(-50%, ${cardY}px)`,
				opacity: cardOp,
				width: 560,
				borderRadius: 40,
				background: `rgba(13, 24, 45, 0.88)`,
				border: `2px solid rgba(197,158,80,0.5)`,
				backdropFilter: 'blur(20px)',
				padding: '36px 48px',
				textAlign: 'center',
				boxShadow: `0 0 80px rgba(197,158,80,${glow}), 0 40px 80px rgba(0,0,0,0.6)`,
			}}>
				<div style={{
					display: 'flex',
					justifyContent: 'space-around',
					alignItems: 'center',
					marginBottom: 24,
				}}>
					<div style={{fontSize: 80}}>🔥</div>
					<div style={{width: 2, height: 80, background: `rgba(197,158,80,0.4)`}} />
					<div style={{fontSize: 80}}>❄️</div>
				</div>
				<div style={{
					fontSize: 48,
					fontFamily: FONT,
					fontWeight: 900,
					color: WHITE,
					letterSpacing: 6,
				}}>
					AURAEASE™
				</div>
				<div style={{
					fontSize: 26,
					fontFamily: FONT,
					color: GOLD,
					letterSpacing: 3,
					marginTop: 10,
					fontWeight: 400,
				}}>
					Dual Thermal Therapy
				</div>
			</div>

			{/* Benefit cascade */}
			<div style={{
				position: 'absolute',
				bottom: '10%',
				width: '100%',
				textAlign: 'center',
				zIndex: 10,
			}}>
				<div style={{opacity: t2Op, fontSize: 58, fontFamily: FONT, fontWeight: 800, color: WHITE, marginBottom: 12}}>
					ONE PATCH.
				</div>
				<div style={{opacity: t2Op, fontSize: 58, fontFamily: FONT, fontWeight: 800, color: GOLD, marginBottom: 20}}>
					BOTH WORLDS.
				</div>
				<div style={{opacity: t3Op, fontSize: 40, fontFamily: FONT, fontWeight: 400, color: 'rgba(255,255,255,0.7)'}}>
					200+ uses · No mess · No appointments
				</div>
			</div>
		</AbsoluteFill>
	);
};

// ── Scene 4 — CTA (110f = 3.7s) ─────────────────────────────────────────────
// Price slam + link in bio pulse
const Scene4: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const priceP   = spring({fps, frame, config: {damping: 38, stiffness: 420, mass: 0.5}});
	const priceScale = interpolate(priceP, [0, 1], [3.5, 1]);
	const priceOp  = interpolate(frame, [0, 5], [0, 1], clamp);

	const sub1Op = interpolate(frame, [18, 32], [0, 1], clamp);
	const sub2Op = interpolate(frame, [34, 48], [0, 1], clamp);

	// Gold glow ring pulse
	const ring = interpolate(Math.sin((frame / 16) * Math.PI), [-1, 1], [0.06, 0.18]);

	// Link in bio pulse
	const linkScale = interpolate(Math.sin((frame / 12) * Math.PI), [-1, 1], [0.97, 1.03]);
	const linkOp   = interpolate(frame, [52, 70], [0, 1], clamp);

	// Fade out at end
	const fadeOut = interpolate(frame, [90, 110], [1, 0], clamp);

	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(circle at 50% 42%, rgba(197,158,80,${ring * 1.5}) 0%, ${NAVY} 55%)`,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				opacity: fadeOut,
			}}
		>
			{/* Try AI background if generated */}
			<BgImage src="bg/bg_victory.jpg" overlay={0.75} />

			{/* Ambient ring */}
			<div style={{
				position: 'absolute',
				width: 680,
				height: 680,
				borderRadius: '50%',
				background: `radial-gradient(circle, rgba(197,158,80,${ring}) 0%, transparent 65%)`,
				border: `1px solid rgba(197,158,80,0.15)`,
			}} />

			{/* Price slam */}
			<div style={{
				transform: `scale(${priceScale})`,
				opacity: priceOp,
				zIndex: 1,
				textAlign: 'center',
			}}>
				<div style={{
					fontSize: 200,
					fontFamily: FONT,
					fontWeight: 900,
					color: GOLD,
					lineHeight: 0.9,
					letterSpacing: -4,
				}}>
					$35
				</div>
			</div>

			<div style={{opacity: sub1Op, zIndex: 1, textAlign: 'center', marginTop: 20}}>
				<div style={{fontSize: 58, fontFamily: FONT, fontWeight: 700, color: WHITE}}>
					200+ USES.
				</div>
			</div>

			<div style={{opacity: sub2Op, zIndex: 1, textAlign: 'center', marginTop: 14}}>
				<div style={{fontSize: 42, fontFamily: FONT, fontWeight: 400, color: 'rgba(255,255,255,0.65)', letterSpacing: 2}}>
					No ice baths. No prescriptions.
				</div>
			</div>

			{/* Divider */}
			<div style={{
				opacity: linkOp,
				width: 220,
				height: 1.5,
				background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
				margin: '32px 0',
				zIndex: 1,
			}} />

			{/* Link in bio */}
			<div style={{
				opacity: linkOp,
				transform: `scale(${linkScale})`,
				zIndex: 1,
				textAlign: 'center',
			}}>
				<div style={{
					fontSize: 64,
					fontFamily: FONT,
					fontWeight: 800,
					color: WHITE,
					letterSpacing: 2,
				}}>
					Link in bio 🔗
				</div>
			</div>

			{/* Brand watermark */}
			<div style={{
				position: 'absolute',
				bottom: 80,
				opacity: sub2Op * 0.6,
				fontSize: 32,
				fontFamily: FONT,
				fontWeight: 400,
				color: WHITE,
				letterSpacing: 8,
			}}>
				AURAEASE™
			</div>
		</AbsoluteFill>
	);
};

// ── Composition: 354 frames = ~11.8s ────────────────────────────────────────
// Scene durations: 70 + 80 + 130 + 110 = 390
// Minus 3 transitions × 12f = 354 total
export const AuraEaseV2: React.FC = () => {
	return (
		<TransitionSeries>
			<TransitionSeries.Sequence durationInFrames={70}>
				<Scene1 />
			</TransitionSeries.Sequence>

			<TransitionSeries.Transition
				timing={springTiming({config: {damping: 80, stiffness: 160}, durationRestThreshold: 0.001})}
				presentation={wipe({direction: 'from-bottom'})}
			/>

			<TransitionSeries.Sequence durationInFrames={80}>
				<Scene2 />
			</TransitionSeries.Sequence>

			<TransitionSeries.Transition
				timing={springTiming({config: {damping: 80, stiffness: 160}, durationRestThreshold: 0.001})}
				presentation={slide({direction: 'from-right'})}
			/>

			<TransitionSeries.Sequence durationInFrames={130}>
				<Scene3 />
			</TransitionSeries.Sequence>

			<TransitionSeries.Transition
				timing={linearTiming({durationInFrames: 18})}
				presentation={fade()}
			/>

			<TransitionSeries.Sequence durationInFrames={110}>
				<Scene4 />
			</TransitionSeries.Sequence>
		</TransitionSeries>
	);
};
