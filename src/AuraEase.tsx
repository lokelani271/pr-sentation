import {
	AbsoluteFill,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
	Series,
} from 'remotion';

const BG = '#1B2A4A';
const WHITE = '#FFFFFF';
const ACCENT = '#4FC3F7';
const FONT = '"Helvetica Neue", Arial, sans-serif';

// Scene 1 (0-2s): Hook
const HookScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const progress = spring({fps, frame, config: {damping: 80, stiffness: 120}});
	const y = interpolate(progress, [0, 1], [80, 0]);
	const opacity = interpolate(frame, [0, 18], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill
			style={{
				background: BG,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				padding: '0 90px',
			}}
		>
			<div style={{opacity, transform: `translateY(${y}px)`, textAlign: 'center'}}>
				<div
					style={{
						fontSize: 76,
						fontFamily: FONT,
						color: WHITE,
						fontWeight: 800,
						lineHeight: 1.3,
					}}
				>
					Still using frozen peas for back pain? 🥶
				</div>
			</div>
		</AbsoluteFill>
	);
};

// Scene 2 (2-5s): "There's a better way." + product mockup
const ProductScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const textOpacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
	const productOpacity = interpolate(frame, [28, 58], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const productScale = spring({fps, frame: frame - 28, config: {damping: 90, stiffness: 110}});

	return (
		<AbsoluteFill
			style={{
				background: BG,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				gap: 64,
				padding: '0 80px',
			}}
		>
			<div style={{opacity: textOpacity, textAlign: 'center'}}>
				<div
					style={{
						fontSize: 80,
						fontFamily: FONT,
						color: WHITE,
						fontWeight: 300,
						fontStyle: 'italic',
						letterSpacing: 1,
					}}
				>
					There's a better way.
				</div>
			</div>

			{/* Product mockup card */}
			<div
				style={{
					opacity: productOpacity,
					transform: `scale(${productScale})`,
					width: 460,
					height: 460,
					borderRadius: 48,
					background: 'linear-gradient(145deg, #213660 0%, #1A2E52 50%, #142440 100%)',
					border: '1.5px solid rgba(79, 195, 247, 0.2)',
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
					flexDirection: 'column',
					boxShadow:
						'0 0 80px rgba(79, 195, 247, 0.1), 0 24px 60px rgba(0,0,0,0.5)',
				}}
			>
				{/* Patch visual */}
				<div
					style={{
						width: 300,
						height: 180,
						borderRadius: 24,
						background:
							'linear-gradient(135deg, #2A4070 0%, #3A5A8A 50%, #1E3358 100%)',
						border: '1.5px solid rgba(79,195,247,0.25)',
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'space-around',
						paddingLeft: 20,
						paddingRight: 20,
					}}
				>
					<div style={{fontSize: 64}}>🔥</div>
					<div
						style={{
							width: 2,
							height: 80,
							background: 'rgba(79,195,247,0.3)',
						}}
					/>
					<div style={{fontSize: 64}}>❄️</div>
				</div>

				<div
					style={{
						color: WHITE,
						fontSize: 32,
						fontFamily: FONT,
						fontWeight: 800,
						letterSpacing: 5,
						marginTop: 28,
					}}
				>
					AURAEASE™
				</div>
				<div
					style={{
						color: ACCENT,
						fontSize: 20,
						fontFamily: FONT,
						fontWeight: 400,
						letterSpacing: 3,
						marginTop: 10,
					}}
				>
					Therapeutic Patch
				</div>
			</div>
		</AbsoluteFill>
	);
};

// Scene 3 (5-9s): 3 animated bullets
const BulletsScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const bullets = [
		{text: 'Hot & Cold therapy', delay: 8},
		{text: 'Reusable 200+ times', delay: 40},
		{text: 'No mess. No appointments.', delay: 72},
	];

	return (
		<AbsoluteFill
			style={{
				background: BG,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				padding: '0 80px',
				gap: 52,
			}}
		>
			{bullets.map(({text, delay}, i) => {
				const localFrame = frame - delay;
				const progress = spring({
					fps,
					frame: localFrame,
					config: {damping: 80, stiffness: 150},
				});
				const x = interpolate(progress, [0, 1], [-140, 0]);
				const opacity = interpolate(localFrame, [0, 18], [0, 1], {
					extrapolateLeft: 'clamp',
					extrapolateRight: 'clamp',
				});

				return (
					<div
						key={i}
						style={{
							opacity,
							transform: `translateX(${x}px)`,
							display: 'flex',
							alignItems: 'center',
							gap: 32,
							width: '100%',
						}}
					>
						<div
							style={{
								width: 64,
								height: 64,
								flexShrink: 0,
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
								fontSize: 40,
							}}
						>
							✅
						</div>
						<div
							style={{
								fontSize: 52,
								fontFamily: FONT,
								color: WHITE,
								fontWeight: 500,
								lineHeight: 1.3,
							}}
						>
							{text}
						</div>
					</div>
				);
			})}
		</AbsoluteFill>
	);
};

// Scene 4 (9-12s): AuraEase™ + CTA
const CTAScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const brandProgress = spring({fps, frame, config: {damping: 80, stiffness: 110}});
	const brandY = interpolate(brandProgress, [0, 1], [70, 0]);
	const brandOpacity = interpolate(frame, [0, 22], [0, 1], {extrapolateRight: 'clamp'});

	const ctaOpacity = interpolate(frame, [32, 55], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const pulse = interpolate(
		Math.sin((frame / 22) * Math.PI),
		[-1, 1],
		[0.97, 1.03],
	);

	return (
		<AbsoluteFill
			style={{
				background: BG,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
			}}
		>
			{/* Ambient glow */}
			<div
				style={{
					position: 'absolute',
					width: 700,
					height: 700,
					borderRadius: '50%',
					background:
						'radial-gradient(circle, rgba(79,195,247,0.07) 0%, transparent 65%)',
					transform: `scale(${pulse})`,
				}}
			/>

			<div
				style={{
					opacity: brandOpacity,
					transform: `translateY(${brandY}px)`,
					textAlign: 'center',
					zIndex: 1,
				}}
			>
				<div
					style={{
						fontSize: 116,
						fontFamily: FONT,
						color: WHITE,
						fontWeight: 800,
						letterSpacing: 2,
						lineHeight: 1,
					}}
				>
					AuraEase™
				</div>

				<div
					style={{
						width: 240,
						height: 2,
						background: `linear-gradient(90deg, transparent, ${ACCENT}, transparent)`,
						margin: '28px auto',
						opacity: ctaOpacity,
					}}
				/>
			</div>

			<div style={{opacity: ctaOpacity, textAlign: 'center', zIndex: 1}}>
				<div
					style={{
						fontSize: 56,
						fontFamily: FONT,
						color: ACCENT,
						fontWeight: 500,
						letterSpacing: 2,
					}}
				>
					Link in bio 🔗
				</div>
			</div>
		</AbsoluteFill>
	);
};

// Wraps a scene with fade-in and fade-out for smooth transitions between Series sequences
const WithFade: React.FC<{duration: number; children: React.ReactNode}> = ({
	duration,
	children,
}) => {
	const frame = useCurrentFrame();
	const opacity = interpolate(
		frame,
		[0, 12, duration - 12, duration - 1],
		[0, 1, 1, 0],
		{extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
	);
	return <AbsoluteFill style={{opacity}}>{children}</AbsoluteFill>;
};

// 60 + 90 + 120 + 90 = 360 frames = 12s
export const AuraEaseVideo: React.FC = () => {
	return (
		<Series>
			<Series.Sequence durationInFrames={60}>
				<WithFade duration={60}>
					<HookScene />
				</WithFade>
			</Series.Sequence>
			<Series.Sequence durationInFrames={90}>
				<WithFade duration={90}>
					<ProductScene />
				</WithFade>
			</Series.Sequence>
			<Series.Sequence durationInFrames={120}>
				<WithFade duration={120}>
					<BulletsScene />
				</WithFade>
			</Series.Sequence>
			<Series.Sequence durationInFrames={90}>
				<WithFade duration={90}>
					<CTAScene />
				</WithFade>
			</Series.Sequence>
		</Series>
	);
};
