import {
	AbsoluteFill,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
	Series,
} from 'remotion';

const PINK = '#FADADD';
const PINK_LIGHT = '#FFF5F5';
const PINK_MID = '#F5C6C9';
const MAUVE = '#8B5E5E';
const ROSE = '#C47C80';
const WHITE = '#FFFFFF';

const Dot: React.FC<{
	size: number;
	top?: string | number;
	bottom?: string | number;
	left?: string | number;
	right?: string | number;
	color: string;
	opacity?: number;
	scale?: number;
}> = ({size, top, bottom, left, right, color, opacity = 1, scale = 1}) => (
	<div
		style={{
			position: 'absolute',
			width: size,
			height: size,
			borderRadius: '50%',
			background: color,
			top,
			bottom,
			left,
			right,
			opacity,
			transform: `scale(${scale})`,
		}}
	/>
);

const IntroScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const logoProgress = spring({fps, frame, config: {damping: 80, stiffness: 150}});
	const logoY = interpolate(logoProgress, [0, 1], [200, 0]);
	const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});
	const subOpacity = interpolate(frame, [35, 60], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const circleScale = spring({fps, frame, config: {damping: 120}});

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(170deg, ${WHITE} 30%, ${PINK} 100%)`,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
			}}
		>
			<Dot size={350} top={-100} right={-80} color={PINK_MID} opacity={0.4} scale={circleScale} />
			<Dot size={180} bottom={200} left={-40} color={PINK_MID} opacity={0.3} scale={circleScale} />
			<Dot size={80} top={300} left={120} color={ROSE} opacity={0.15} scale={circleScale} />

			<div
				style={{
					opacity: logoOpacity,
					transform: `translateY(${logoY}px)`,
					textAlign: 'center',
				}}
			>
				<div
					style={{
						fontSize: 120,
						fontFamily: 'Georgia, "Times New Roman", serif',
						color: MAUVE,
						letterSpacing: 12,
						fontStyle: 'italic',
						fontWeight: 'normal',
						lineHeight: 1,
					}}
				>
					Leibeauty
				</div>

				<div style={{opacity: subOpacity, marginTop: 32, textAlign: 'center'}}>
					<div
						style={{
							width: 160,
							height: 1.5,
							background: ROSE,
							margin: '0 auto 28px',
						}}
					/>
					<div
						style={{
							fontSize: 32,
							fontFamily: 'Georgia, serif',
							color: ROSE,
							letterSpacing: 8,
						}}
					>
						SKINCARE · TAHITI
					</div>
					<div style={{fontSize: 52, marginTop: 16}}>🌺</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};

const ProductScene: React.FC<{
	emoji: string;
	title: string;
	subtitle: string;
	description: string;
	bg: string;
}> = ({emoji, title, subtitle, description, bg}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const emojiScale = spring({fps, frame, config: {damping: 80, stiffness: 180}});

	const titleProgress = spring({fps, frame: frame - 8, config: {damping: 100}});
	const titleX = interpolate(titleProgress, [0, 1], [-300, 0]);
	const titleOpacity = interpolate(frame, [8, 28], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const lineWidth = interpolate(frame, [18, 48], [0, 200], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const descOpacity = interpolate(frame, [30, 55], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				background: bg,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
				padding: '0 100px',
			}}
		>
			<Dot size={450} top={-180} right={-120} color="rgba(255,255,255,0.35)" opacity={1} />
			<Dot size={200} bottom={80} left={-60} color="rgba(255,200,205,0.4)" opacity={1} />

			<div
				style={{
					fontSize: 200,
					transform: `scale(${emojiScale})`,
					marginBottom: 50,
					filter: 'drop-shadow(0 16px 40px rgba(180,100,100,0.15))',
					lineHeight: 1,
				}}
			>
				{emoji}
			</div>

			<div
				style={{
					opacity: titleOpacity,
					transform: `translateX(${titleX}px)`,
					textAlign: 'center',
					width: '100%',
				}}
			>
				<div
					style={{
						fontSize: 80,
						fontFamily: 'Georgia, serif',
						color: MAUVE,
						fontStyle: 'italic',
						letterSpacing: 4,
						lineHeight: 1.1,
					}}
				>
					{title}
				</div>

				<div
					style={{
						width: lineWidth,
						height: 2,
						background: ROSE,
						margin: '18px auto',
					}}
				/>

				<div
					style={{
						fontSize: 28,
						fontFamily: 'Georgia, serif',
						color: ROSE,
						letterSpacing: 8,
					}}
				>
					{subtitle}
				</div>
			</div>

			<div
				style={{
					opacity: descOpacity,
					textAlign: 'center',
					fontSize: 34,
					color: '#A07878',
					fontFamily: 'Georgia, serif',
					lineHeight: 1.7,
					maxWidth: 760,
					marginTop: 28,
					fontStyle: 'italic',
				}}
			>
				{description}
			</div>
		</AbsoluteFill>
	);
};

const CTAScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const pulse = interpolate(Math.sin((frame / 18) * Math.PI), [-1, 1], [0.92, 1.08]);

	const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});
	const tagOpacity = interpolate(frame, [18, 38], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const ctaOpacity = interpolate(frame, [32, 52], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(170deg, ${PINK} 0%, ${WHITE} 60%, ${PINK_LIGHT} 100%)`,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				flexDirection: 'column',
			}}
		>
			<div
				style={{
					position: 'absolute',
					width: 700,
					height: 700,
					borderRadius: '50%',
					border: `2px solid ${ROSE}`,
					opacity: 0.12,
					transform: `scale(${pulse})`,
				}}
			/>
			<div
				style={{
					position: 'absolute',
					width: 520,
					height: 520,
					borderRadius: '50%',
					border: `2px solid ${ROSE}`,
					opacity: 0.1,
					transform: `scale(${2 - pulse})`,
				}}
			/>

			<Dot size={300} top={-80} left={-80} color={PINK_MID} opacity={0.3} />
			<Dot size={200} bottom={100} right={-60} color={PINK_MID} opacity={0.25} />

			<div style={{opacity: logoOpacity, textAlign: 'center'}}>
				<div
					style={{
						fontSize: 100,
						fontFamily: 'Georgia, serif',
						color: MAUVE,
						fontStyle: 'italic',
						letterSpacing: 10,
					}}
				>
					Leibeauty
				</div>
				<div style={{fontSize: 56, marginTop: 12}}>🌸</div>
			</div>

			<div style={{opacity: tagOpacity, textAlign: 'center', marginTop: 40}}>
				<div
					style={{
						fontSize: 42,
						color: ROSE,
						fontFamily: 'Georgia, serif',
						letterSpacing: 3,
						marginBottom: 16,
					}}
				>
					@leibeauty
				</div>
				<div
					style={{
						width: 120,
						height: 1.5,
						background: PINK_MID,
						margin: '0 auto',
					}}
				/>
			</div>

			<div
				style={{
					opacity: ctaOpacity,
					textAlign: 'center',
					marginTop: 24,
				}}
			>
				<div
					style={{
						fontSize: 34,
						color: '#B09090',
						fontFamily: 'Georgia, serif',
						letterSpacing: 2,
						fontStyle: 'italic',
					}}
				>
					Découvrez la boutique ✨
				</div>
				<div
					style={{
						fontSize: 34,
						color: '#B09090',
						fontFamily: 'Georgia, serif',
						letterSpacing: 2,
						fontStyle: 'italic',
						marginTop: 8,
					}}
				>
					lien en bio
				</div>
			</div>
		</AbsoluteFill>
	);
};

export const LeibeautyVideo: React.FC = () => {
	return (
		<Series>
			<Series.Sequence durationInFrames={90}>
				<IntroScene />
			</Series.Sequence>
			<Series.Sequence durationInFrames={75}>
				<ProductScene
					emoji="💎"
					title="Gua Sha"
					subtitle="FACIAL TOOL"
					description="Sculptez votre visage, révélez votre éclat naturel"
					bg={`linear-gradient(160deg, ${PINK_LIGHT} 0%, ${PINK} 100%)`}
				/>
			</Series.Sequence>
			<Series.Sequence durationInFrames={75}>
				<ProductScene
					emoji="🧊"
					title="Ice Roller"
					subtitle="GLOW BOOSTER"
					description="Dégonflée, lumineuse, rafraîchie — en 60 secondes"
					bg={`linear-gradient(160deg, ${WHITE} 0%, #EBF4F8 100%)`}
				/>
			</Series.Sequence>
			<Series.Sequence durationInFrames={75}>
				<ProductScene
					emoji="🌸"
					title="Masques"
					subtitle="FACE MASKS"
					description="Nourrissez votre peau avec des ingrédients naturels de Tahiti"
					bg={`linear-gradient(160deg, ${PINK} 0%, ${WHITE} 100%)`}
				/>
			</Series.Sequence>
			<Series.Sequence durationInFrames={60}>
				<CTAScene />
			</Series.Sequence>
		</Series>
	);
};
