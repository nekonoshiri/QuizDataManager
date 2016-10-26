

class MojiUtil(object):
    hankakuList = '0123456789'\
        'abcdefghijklmnopqrstuvwxyz'\
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
        '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    hankakuListSP = hankakuList + ' '

    zenkakuList = '０１２３４５６７８９'\
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'\
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'\
        '！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜'

    zenkakuListSP = zenkakuList + '\u3000'

    @classmethod
    def toZenkaku(cls, hankaku, space = False):
        hl = cls.hankakuListSP if space else cls.hankakuList
        zl = cls.zenkakuListSP if space else cls.zenkakuList
        transdict = str.maketrans(hl, zl)
        return hankaku.translate(transdict)


    @classmethod
    def toHankaku(cls, zenkaku, space = False):
        hl = cls.hankakuListSP if space else cls.hankakuList
        zl = cls.zenkakuListSP if space else cls.zenkakuList
        transdict = str.maketrans(zl, hl)
        return zenkaku.translate(transdict)

