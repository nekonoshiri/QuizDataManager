from enum import Enum

from dbmanip import QuestionDataDBManip
from interactive import ItraWithQD
from register import Register, QuizType


class ContinueType (Enum):
    FINISH = '終了'
    RESTART = '同サブジャンル・同形式'
    CHANGE_TYPE = '形式を変える'
    CHANGE_SUBGENRE = 'サブジャンルを変える'
    CHANGE_GENRE = 'ジャンルを変える'
    CHANGE_TYPEGENRE = '形式とジャンルを変える'


def mainLoop (qdManip):
    genreId = None
    quizTypeRegister = None
    while True:
        if genreId is None:
            itraWithQD = ItraWithQD (qdManip)
            genreId = itraWithQD.inputGenre ()
            subGenreId = itraWithQD.inputSubGenre (genreId)
            examGenreId = itraWithQD.inputExamGenre (genreId)

        if subGenreId is None:
            subGenreId = itraWithQD.inputSubGenre (genreId)

        if quizTypeRegister is None:
            quizTypeRegister = ItraWithQD.inputQuizType (list (QuizType))

        register = quizTypeRegister (genreId, subGenreId, examGenreId)
        register.registerMain (qdManip)

        continueType = ItraWithQD.inputForContinue (list (ContinueType))
        if continueType == ContinueType.FINISH:
            break;
        if continueType == ContinueType.CHANGE_TYPE:
            quizTypeRegister = None
        if continueType == ContinueType.CHANGE_SUBGENRE:
            subGenreId = None
        if continueType == ContinueType.CHANGE_GENRE:
            genreId = None
        if continueType == ContinueType.CHANGE_TYPEGENRE:
            genreId = None
            quizTypeRegister = None


def main ():
    qdManip = QuestionDataDBManip ('question_data.sqlite3')
    mainLoop (qdManip)
    qdManip.close ()


if __name__ == '__main__':
    main ()
