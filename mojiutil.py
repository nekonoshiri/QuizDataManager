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


    @staticmethod
    def isHiragana(text, doublehyphen = False, nakaguro = False,
            onbiki = False, odoriji = False, gouji = False):
        for c in text:
            if '\u3041' <= c <= '\u3096':
                continue
            if doublehyphen and c == '\u30A0':
                continue
            if nakaguro and c == '\u30FB':
                continue
            if onbiki and c == '\u30FC':
                continue
            if odoriji and '\u309D' <= c <= '\u309E':
                continue
            if gouji and c == '\u309F':
                continue
            return False
        return True


    @staticmethod
    def isZenkakuKatakana(text, doublehyphen = False, nakaguro = False,
            onbiki = False, odoriji = False, gouji = False):
        for c in text:
            if '\u30A1' <= c <= '\u30FA':
                continue
            if doublehyphen and c == '\u30A0':
                continue
            if nakaguro and c == '\u30FB':
                continue
            if onbiki and c == '\u30FC':
                continue
            if odoriji and '\u30FD' <= c <= '\u30FE':
                continue
            if gouji and c == '\u30FF':
                continue
            return False
        return True

