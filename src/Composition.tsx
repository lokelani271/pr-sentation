import {
	AbsoluteFill,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

export const MyComp: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();

	const opacity = interpolate(frame, [0, 30], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const scale = spring({
		fps,
		frame,
		config: {damping: 200},
	});

	return (
		<AbsoluteFill
			style={{
				background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
			}}
		>
			<div
				style={{
					opacity,
					transform: `scale(${scale})`,
					color: 'white',
					fontSize: 80,
					fontFamily: 'sans-serif',
					fontWeight: 'bold',
					textAlign: 'center',
				}}
			>
				Hello Remotion!
				<div style={{fontSize: 40, marginTop: 20, opacity: 0.7}}>
					Frame {frame} / {durationInFrames}
				</div>
			</div>
		</AbsoluteFill>
	);
};
