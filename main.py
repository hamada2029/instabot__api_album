from argparse import ArgumentParser
import mimetypes
from PIL import Image
import tempfile

from api_album import MyBot, as_medias


def run(fps, u, p, c):
    bot = MyBot()
    bot.login(
        username=u,
        password=p
    )

    if len(fps) == 1:
        fp = fps[0]
        mime = mimetypes.guess_type(fp)[0]
        if not mime.endswith('jpeg'):
            im = Image.open(fp)
            im = im.convert('RGB')
            with tempfile.TemporaryDirectory() as tdr:
                fp = tdr + '/instabot_tmp.jpg'
                im.save(fp, format='JPEG', dpi=(72, 72))
                ret = bot.upload_photo(fp, caption=c)
    else:
        medias = as_medias(fps)
        ret = bot.upload_album(medias, caption=c)
    print(ret)


def main():
    """Main."""
    parser = ArgumentParser(
        description='Post multiple images to Instagram.'
    )
    parser.add_argument(
        'fps', type=str, nargs='+',
        help='image path strings'
    )
    parser.add_argument('-u', required=True, help='username')
    parser.add_argument('-p', required=True, help='password')
    parser.add_argument('-c', help='caption')
    args = parser.parse_args()

    run(args.fps, args.u, args.p, args.c)


if __name__ == '__main__':
    main()
