import time
from uuid import uuid4
import random
import json
from PIL import Image
from pathlib import Path
import mimetypes
import io
from instabot.api import config
from instabot import Bot


def just_upload_photo(
    self,
    photo_data
):
    """
    photo_data must be compatible_aspect_ratio
    """
    upload_id = str(int(time.time() * 1000))
    waterfall_id = str(uuid4())
    # upload_name example: '1576102477530_0_7823256191'
    upload_name = "{upload_id}_0_{rand}".format(
        upload_id=upload_id, rand=random.randint(1000000000, 9999999999)
    )
    rupload_params = {
        "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
        "media_type": "1",
        "xsharing_user_ids": "[]",
        "upload_id": upload_id,
        "image_compression": json.dumps(
            {"lib_name": "moz", "lib_version": "3.1.m", "quality": "80"}
        ),
    }
    photo_len = str(len(photo_data))
    self.api.session.headers.update(
        {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X_FB_PHOTO_WATERFALL_ID": waterfall_id,
            "X-Entity-Type": "image/jpeg",
            "Offset": "0",
            "X-Entity-Name": upload_name,
            "X-Entity-Length": photo_len,
            "Content-Type": "application/octet-stream",
            "Content-Length": photo_len,
            "Accept-Encoding": "gzip",
        }
    )
    response = self.api.session.post(
        "https://{domain}/rupload_igphoto/{name}".format(
            domain=config.API_DOMAIN, name=upload_name
        ),
        data=photo_data,
    )
    if response.status_code != 200:
        self.api.logger.error(
            "Photo Upload failed with the following response: {}".format(response)
        )
        response.raise_for_status()
    return upload_id


def photo_metadata(self, upload_id, size):
    width, height = size
    return {
        "media_folder": "Instagram",
        "source_type": 4,
        "upload_id": upload_id,
        "device": self.api.device_settings,
        "edits": {
            "crop_original_size": [width * 1.0, height * 1.0],
            "crop_center": [0.0, 0.0],
            "crop_zoom": 1.0,
        },
        "extra": {"source_width": width, "source_height": height}
    }


def just_upload_video(
    self, video_data, thumbnail, duration, size
):
    """not work"""
    width, height = size
    upload_id = str(int(time.time() * 1000))
    waterfall_id = str(uuid4())
    # upload_name example: '1576102477530_0_7823256191'
    upload_name = "{upload_id}_0_{rand}".format(
        upload_id=upload_id, rand=random.randint(1000000000, 9999999999)
    )
    rupload_params = {
        "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
        "media_type": "2",
        "xsharing_user_ids": "[]",
        "upload_id": upload_id,
        "upload_media_duration_ms": str(int(duration * 1000)),
        "upload_media_width": str(width),
        "upload_media_height": str(height),
    }
    self.api.session.headers.update(
        {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X_FB_VIDEO_WATERFALL_ID": waterfall_id,
            "X-Entity-Type": "video/mp4",
        }
    )
    response = self.api.session.get(
        "https://{domain}/rupload_igvideo/{name}".format(
            domain=config.API_DOMAIN, name=upload_name
        )
    )
    if response.status_code != 200:
        return False
    video_len = str(len(video_data))
    self.api.session.headers.update(
        {
            "Offset": "0",
            "X-Entity-Name": upload_name,
            "X-Entity-Length": video_len,
            "Content-Type": "application/octet-stream",
            "Content-Length": video_len,
        }
    )
    response = self.api.session.post(
        "https://{domain}/rupload_igvideo/{name}".format(
            domain=config.API_DOMAIN, name=upload_name
        ),
        data=video_data,
    )
    response.raise_for_status()
    return upload_id


def video_metadata(self, upload_id, duration, size):
    width, height = size
    return {
        "upload_id": upload_id,
        "source_type": 4,
        "poster_frame_index": 0,
        "length": duration,
        "audio_muted": False,
        "filter_type": 0,
        "date_time_original": time.strftime("%Y:%m:%d %H:%M:%S", time.localtime()),
        "timezone_offset": "10800",
        "width": width,
        "height": height,
        "clips": [{"length": duration, "source_type": "4"}],
        "extra": {"source_width": width, "source_height": height},
        "device": self.api.device_settings,
    }


def upload_album(
    self,
    medias,
    caption=None,
    **kwargs
):
    """
    from post_album of instagram_private_api
    medias = [
        {"type": "image", "size": (720, 720), "data": "..."},
        {
            "type": "image", "size": (720, 720),
            "usertags": [{"user_id":4292127751, "position":[0.625347,0.4384531]}],
            "data": "..."
        },
        {"type": "video", "size": (720, 720), "duration": 12.4, "thumbnail": "...", "data": "..."}
    ]
    media data must be compatible_aspect_ratio
    """
    album_upload_id = str(int(time.time() * 1000))
    children_metadata = []

    for media in medias:
        if len(children_metadata) >= 10:
            continue
        if media.get('type', '') not in ['image', 'video']:
            raise ValueError(
                'Invalid media type: {0!s}'.format(
                    media.get('type', '')
                )
            )
        if not media.get('data'):
            raise ValueError('Data not specified.')
        if not media.get('size'):
            raise ValueError('Size not specified.')
        if media['type'] == 'video':
            if not media.get('duration'):
                raise ValueError('Duration not specified.')
            if not media.get('thumbnail'):
                raise ValueError('Thumbnail not specified.')
        aspect_ratio = (media['size'][0] * 1.0) / (media['size'][1] * 1.0)
        if aspect_ratio > 1.0 or aspect_ratio < 1.0:
            raise ValueError('Invalid media aspect ratio.')

        if media['type'] == 'video':
            raise ValueError('can not upload video for now.')
            # upload_id = self.just_upload_video(media['data'], media['thumbnail'], media['duration'], media['size'])
            # print('upload_id:', upload_id)
            # metadata = self.video_metadata(upload_id, media['duration'], media['size'])
        else:
            upload_id = self.just_upload_photo(media['data'])
            print('upload_id:', upload_id)
            metadata = self.photo_metadata(upload_id, media['size'])
            if media.get('usertags'):
                usertags = media['usertags']
                utags = {'in': [{'user_id': str(u['user_id']), 'position': u['position']} for u in usertags]}
                metadata['usertags'] = json.dumps(utags, separators=(',', ':'))
        children_metadata.append(metadata)

    if len(children_metadata) <= 1:
        raise ValueError('Invalid number of media objects: {0:d}'.format(len(children_metadata)))

    album_upload_id = str(int(time.time() * 1000))
    params = {
        'caption': caption,
        'client_sidecar_id': album_upload_id,
        'children_metadata': children_metadata
    }
    disable_comments = kwargs.pop('disable_comments', False)
    if disable_comments:
        params['disable_comments'] = '1'

    json_params = json.dumps(params, separators=(',', ':'))
    ret = self.api.send_request('media/configure_sidecar/', post=json_params)
    print(self.last_json)
    return ret


def as_medias(filepaths):
    medias = []
    for fp in filepaths:
        mime = mimetypes.guess_type(fp)[0]
        tp = mime.split('/')[0]
        if tp == 'image':
            im = Image.open(fp)
            if not mime.endswith('jpeg'):
                im = im.convert('RGB')
                op = io.BytesIO()
                im.save(op, format='JPEG', dpi=(72, 72))
                s = op.getvalue()
            else:
                s = Path(fp).read_bytes()
            medias.append(
                {'type': 'image', 'size': im.size, 'data': s}
            )
        elif tp == 'video':
            pass
            # s = Path(fp).read_bytes()
            # medias.append(
            #     {'type': 'video', 'size': (700, 700), 'data': s, 'duration': 2.94, 'thumbnail': b''}
            # )
    return medias


class MyBot(Bot):
    def just_upload_photo(self, photo_data):
        return just_upload_photo(self, photo_data)

    def photo_metadata(self, upload_id, size):
        return photo_metadata(self, upload_id, size)

    def just_upload_video(
        self, video_data, thumbnail, duration, size
    ):
        return just_upload_video(
            self, video_data, thumbnail, duration, size
        )

    def video_metadata(self, upload_id, duration, size):
        return video_metadata(self, upload_id, duration, size)

    def upload_album(self, medias, caption=None, **kwargs):
        return upload_album(self, medias, caption=None, **kwargs)


def main():
    """Main."""


if __name__ == '__main__':
    main()
