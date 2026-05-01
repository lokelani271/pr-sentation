import {Composition} from 'remotion';
import {MyComp} from './Composition';
import {LeibeautyVideo} from './Leibeauty';
import {AuraEaseVideo} from './AuraEase';
import {AuraEaseV2} from './AuraEaseV2';

export const Root: React.FC = () => {
	return (
		<>
			<Composition
				id="MyComp"
				component={MyComp}
				durationInFrames={120}
				width={1920}
				height={1080}
				fps={30}
				defaultProps={{}}
			/>
			<Composition
				id="Leibeauty"
				component={LeibeautyVideo}
				durationInFrames={375}
				width={1080}
				height={1920}
				fps={30}
				defaultProps={{}}
			/>
			<Composition
				id="AuraEase"
				component={AuraEaseVideo}
				durationInFrames={360}
				width={1080}
				height={1920}
				fps={30}
				defaultProps={{}}
			/>
			<Composition
				id="AuraEaseV2"
				component={AuraEaseV2}
				durationInFrames={354}
				width={1080}
				height={1920}
				fps={30}
				defaultProps={{}}
			/>
		</>
	);
};
