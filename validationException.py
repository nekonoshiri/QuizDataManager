class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


class GenreNoneError(ValidationError):
    def __init__(self):
        super().__init__('ジャンルを入力してね！')


class SubGenreNoneError(ValidationError):
    def __init__(self):
        super().__init__('サブジャンルを入力してね！')


class ExamGenreNoneError(ValidationError):
    def __init__(self):
        super().__init__('検定ジャンルを入力してね！')


class SeriesIdNoneError(ValidationError):
    def __init__(self):
        super().__init__('回収シリーズを入力してね！')


class QuestionBlankError(ValidationError):
    def __init__(self):
        super().__init__('問題を入力してね！')


class AnswerBlankError(ValidationError):
    def __init__(self):
        super().__init__('答えを入力してね！')


class StableTypeUndefinedError(ValidationError):
    def __init__(self):
        super().__init__('安定性を入力してね！')


class InvalidPictureIdError(ValidationError):
    def __init__(self):
        super().__init__('画像IDは整数値を入力してね！')


class AssocLengthError(ValidationError):
    def __init__(self):
        super().__init__('連想のヒントは4つまでだよ！')


class PanelLengthError(ValidationError):
    def __init__(self):
        super().__init__('パネルの数は8枚か10枚にしてね！')


class PanelLengthInconsistError(ValidationError):
    def __init__(self):
        super().__init__('答えの文字数は統一してね！')


class PanelNoAnswerError(ValidationError):
    def __init__(self):
        super().__init__('パネルから作れない答えがあるよ！')


class SlotStrLenError(ValidationError):
    def __init__(self):
        super().__init__('答えと各ダミーの文字数は全て同じにしてね！')


class AnswerLengthOverError(ValidationError):
    def __init__(self):
        super().__init__('答えが長すぎるよ！')


class TypingTypeInconsistError(ValidationError):
    def __init__(self):
        super().__init__('答えはひらがな・カタカナ・英数字で統一してね！')

