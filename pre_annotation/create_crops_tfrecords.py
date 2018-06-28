from os.path import join
import PIL.Image
import tensorflow as tf
from tqdm import tqdm

from rare.utils import dataset_util
from rare.core import standard_fields as fields

flags = tf.app.flags
flags.DEFINE_string('data_dir', '', 'Root directory of crops.')
flags.DEFINE_string('output_path', '', 'Path to the output TFRecord.')
FLAGS = flags.FLAGS


def main(_):
  writer = tf.python_io.TFRecordWriter(FLAGS.output_path)

  list_file_path = join(FLAGS.data_dir, 'crops_list.txt')
  with open(list_file_path, 'r') as f:
    image_path_list = f.readlines()

  for image_rel_path in tqdm(image_path_list):
    image_path = join(FLAGS.data_dir, image_rel_path)

    # write example
    example = tf.train.Example(features=tf.train.Features(feature={
      fields.TfExampleFields.image_encoded: \
        dataset_util.bytes_feature(image_jpeg),
      fields.TfExampleFields.image_format: \
        dataset_util.bytes_feature('jpeg'.encode('utf-8')),
      fields.TfExampleFields.filename: \
        dataset_util.bytes_feature(image_rel_path.encode('utf-8')),
      fields.TfExampleFields.channels: \
        dataset_util.int64_feature(3),
      fields.TfExampleFields.colorspace: \
        dataset_util.bytes_feature('rgb'.encode('utf-8'))
    }))
    writer.write(example.SerializeToString())

  writer.close()

if __name__ == '__main__':
  tf.app.run()
