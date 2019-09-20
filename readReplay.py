import csv, glob, importlib, mpyq, six, json, os, sys, time
from absl import flags
from scipy import sparse
from pysc2 import maps, run_configs
from pysc2.env import sc2_env, run_loop
from pysc2.lib import features, remote_controller
from s2clientprotocol import sc2api_pb2 as sc_pb

# local features
screen_features = ['height_map', 'visibility_map', 'creep', 'power', 'player_id', 'player_relative',
				   'unit_type', 'selected', 'unit_hit_point', 'unit_hit_point_ratio', 'unit_energy',
				   'unit_energy_ratio', 'unit_shield', 'unit_shield_ratio', 'unit_density',
				   'unit_density_ratio', 'effects']
# global features
minimap_features = ['height_map', 'visibility_map', 'creep', 'camera', 'player_id', 'player_relative', 'selected']
# non-spatial features
other_features = ['player', 'game_loop', 'score_cumulative', 'available_actions', 'single_select',
				  'multi_select', 'cargo', 'cargo_slots_available', 'build_queue', 'control_groups']

def csr_matrix_to_list(sparse_matrix):
	return [sparse_matrix.data.tolist(),
	sparse_matrix.indices.tolist(),
	sparse_matrix.indptr.tolist()] 

flags.DEFINE_string (		 'replay_dir', default=r'/home/adamschunk/StarCraftII/Replays/local', help='')
flags.DEFINE_string (		 'output_dir', default=r'C:/develop/Sc2ReplayReader', help='')
flags.DEFINE_integer(				'fps', default=30,	help='')
flags.DEFINE_bool   (		 'fog_of_war', default=True,  help='')
flags.DEFINE_integer(	'observed_player', default=1,	 help='')
flags.DEFINE_integer('feature_screen_size', default=84,	help='')
flags.DEFINE_integer(	 'feature_minimap', default=64,	help='')
flags.DEFINE_bool   (   'use_feature_units', default=True, help='')
flags.DEFINE_integer(	  		'step_size', default=8,	help='')

def get_game_version(replay):
	replay_io = six.BytesIO()
	replay_io.write(replay)
	replay_io.seek(0)
	archive = mpyq.MPQArchive(replay_io).extract()
	metadata = json.loads(archive[b'replay.gamemetadata.json'].decode('utf-8'))
	version = metadata['GameVersion']
	return '.'.join(version.split('.')[:-1])

def parse(replay):
	print("test")
	run_config = run_configs.get()

	interface = sc_pb.InterfaceOptions()
	interface.score = True
	interface.feature_layer.resolution.x = flags.feature_screen_size
	interface.feature_layer.resolution.y = flags.feature_screen_size
	interface.feature_layer.minimap_resolution.x = flags.feature_minimap
	interface.feature_layer.minimap_resolution.y = flags.feature_minimap

	replay_data = run_config.replay_data(replay)
	start_replay = sc_pb.RequestStartReplay(
				   replay_data=replay_data,
				   options=interface,
				   disable_fog=not flags.fog_of_war,
				   observed_player_id=flags.observed_player)
	game_version = get_game_version(replay_data)

	print('StarCraft II', game_version, 'Replay Parser')

	with run_config.start(game_version=game_version) as controller:
		info = controller.replay_info(replay_data)
		map_path = info.local_map_path
		if map_path: start_replay.map_data = run_config.map_data(map_path)
		controller.start_replay(start_replay)

		print('REPLAY'.center(60,'_'))
		print(info)
		print(map_path)
		print('_' * 60)
		try:
			print("******************")
			game_info = controller.game_info()
			
			print(game_info)
			print("******************")
			print(game_info.start_raw.map_size)
			print("******************")
			feat = features.features_from_game_info(controller.game_info(), use_feature_units=flags.use_feature_units)
			while True:
				beg = time.time()

				controller.step(flags.step_size)
				obs = controller.observe()
				obs_t = feat.transform_obs(obs)

				id = replay.split('\\')[-1].split('.')[0] + '_player_{}'.format(flags.observed_player)
				datafold = os.path.join(flags.output_dir, id)
				if not os.path.exists(datafold):
					os.makedirs(datafold)

				# screen features
				for i in range(len(screen_features)):
					with open(os.path.join(datafold, 'screen_{}_.txt'.format(screen_features[i])), 'a+', newline='') as f:
						writer = csv.writer(f)
						writer.writerows(csr_matrix_to_list(sparse.csr_matrix(obs_t['feature_screen'][i])))

				# minimap features
				for i in range(len(minimap_features)):
					with open( os.path.join(datafold, 'minimap_{}_.txt'.format(minimap_features[i])), 'a+', newline='') as f:
						writer = csv.writer(f)
						writer.writerows(csr_matrix_to_list(sparse.csr_matrix(obs_t['feature_minimap'][i])))

				# non-spatial features
				for i in other_features:
					with open(os.path.join(datafold, '{}.txt'.format(i)), 'a+', newline='') as f:
						writer = csv.writer(f)
						writer.writerows([obs_t[i]])

				# actions
				for action in obs.actions:
					try:
						func = feat.reverse_action(action).function
						args = feat.reverse_action(action).arguments
						with open(os.path.join(datafold, 'actions.txt'), 'a+', newline='') as f:
							writer = csv.writer(f)
							writer.writerows([obs_t['game_loop'].tolist(), [func], [args]])
					except ValueError:
						pass

				if obs.player_result: break

				time.sleep(max(0, beg + 1 / flags.fps - time.time()))
		except KeyboardInterrupt:
			pass

		print( 'score:', obs.observation.score.score)
		print('result:', obs.player_result)
		print()

if __name__ == '__main__':
	flags = flags.FLAGS
	flags(sys.argv)
	
	print('{}/*.SC2Replay'.format(flags.replay_dir))
	for replay in glob.glob('{}/*.SC2Replay'.format(flags.replay_dir)): parse(replay)