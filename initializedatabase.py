import sqlite3

def initializeDatabase():
    databaseName = 'question_data.sqlite3'

    conn = sqlite3.connect(databaseName)
    cs = conn.cursor()
    cs.executescript("""
create table genre (id integer primary key not null unique, genre text not null unique);
create table subgenre(id integer primary key not null unique, subgenre text not null, genre integer not null, foreign key(genre) references genre(id));
create table examgenre (id integer primary key not null unique, examgenre text not null unique);
create table assoctype (id integer primary key not null unique, assoctype text not null unique);
create table typingtype (id integer primary key not null unique, typingtype text not null unique);
create table multitype(id integer primary key not null unique, multitype text not null unique);
create table series (id integer primary key not null unique, series text not null unique);
create table stable (id integer primary key not null unique, stable text not null unique);
create table quiz_ox(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer integer not null check(answer in (0, 1)), comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_four(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, dummy1 text not null, dummy2 text not null, dummy3 text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_assoc(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question1 text not null, question2 text not null, question3 text not null, question4 text not null, answer text not null, dummy1 text not null, dummy2 text not null, dummy3 text not null, assoctype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(assoctype) references assoctype(id));
create table quiz_sort(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_panel(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, panel text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_slot(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, dummy1 text not null, dummy2 text not null, dummy3 text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_typing(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, typingtype integer not null, answer text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_cube(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, typingtype integer not null, answer text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_effect(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null, questionEffect text not null, typingtype integer not null, answer text not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
create table quiz_order(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, multitype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(multitype) references multitype(id));
create table quiz_connect(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, option_left text not null, option_right text not null, multitype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(multitype) references multitype(id));
create table quiz_multi(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, dummy text not null, multitype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(multitype) references multitype(id));
create table quiz_group(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, group1 text not null, group2 text not null, group3 text not null, multitype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(multitype) references multitype(id));
create table quiz_firstcome(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, answer text not null, dummy text not null, multitype integer not null, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id), foreign key(multitype) references multitype(id));
create table quiz_imagetouch(id integer primary key not null unique, subgenre integer not null, examgenre integer not null, difficulty_min integer not null check((1 <= difficulty_min) and (difficulty_min <= 5)) default 1, difficulty_max integer not null check((difficulty_min <= difficulty_max) and (difficulty_max <= 5)) default 5, question text not null unique, comment text not null default '', stable integer not null check(stable in (0, 1)) default 0, appear_count integer not null check(0 <= appear_count) default 1, solve_count integer not null check((0 <= solve_count) and (solve_count <= appear_count)) default 0, accuracy integer not null check((0 <= accuracy) and (accuracy <= 100)) default 0, series integer not null, picture_id integer, picture_answer_id integer, foreign key(subgenre) references subgenre(id), foreign key(examgenre) references examgenre(id), foreign key(series) references series(id));
insert into genre values(0, 'ジャンル不明');
insert into genre values(1, 'ノンジャンル');
insert into genre values(2, 'アニメ＆ゲーム');
insert into genre values(3, 'スポーツ');
insert into genre values(4, '芸能');
insert into genre values(5, 'ライフスタイル');
insert into genre values(6, '社会');
insert into genre values(7, '文系学問');
insert into genre values(8, '理系学問');
insert into genre values(9, '検定オンリー');
insert into subgenre values(0, 'サブジャンル不明', 0);
insert into subgenre values(1, 'ノンジャンル', 1);
insert into subgenre values(2, 'アニメ・特撮', 2);
insert into subgenre values(3, '漫画・ノベル', 2);
insert into subgenre values(4, 'ゲーム・おもちゃ', 2);
insert into subgenre values(5, 'サブジャンル不明', 2);
insert into subgenre values(6, '野球', 3);
insert into subgenre values(7, 'サッカー', 3);
insert into subgenre values(8, 'スポーツその他', 3);
insert into subgenre values(9, 'サブジャンル不明', 3);
insert into subgenre values(10, 'テレビ・映画', 4);
insert into subgenre values(11, '音楽', 4);
insert into subgenre values(12, '芸能その他', 4);
insert into subgenre values(13, 'サブジャンル不明', 4);
insert into subgenre values(14, 'グルメ・生活', 5);
insert into subgenre values(15, 'ホビー', 5);
insert into subgenre values(16, 'ライフスタイルその他', 5);
insert into subgenre values(17, 'サブジャンル不明', 5);
insert into subgenre values(18, '地理', 6);
insert into subgenre values(19, '政治・経済', 6);
insert into subgenre values(20, '社会その他', 6);
insert into subgenre values(21, 'サブジャンル不明', 6);
insert into subgenre values(22, '歴史', 7);
insert into subgenre values(23, '美術・文学', 7);
insert into subgenre values(24, '文系学問その他', 7);
insert into subgenre values(25, 'サブジャンル不明', 7);
insert into subgenre values(26, '物理・化学', 8);
insert into subgenre values(27, '生物', 8);
insert into subgenre values(28, '理系学問その他', 8);
insert into subgenre values(29, 'サブジャンル不明', 8);
insert into subgenre values(30, '検定オンリー', 9);
insert into examgenre values(1, '検定未収録');
insert into assoctype values(0, '順番不明');
insert into assoctype values(1, '順番固定');
insert into assoctype values(2, '3ヒントランダム');
insert into assoctype values(3, '4ヒントランダム');
insert into typingtype values(1, 'ひらがな');
insert into typingtype values(2, 'カタカナ');
insert into typingtype values(3, '英数字');
insert into multitype values(0, '不明');
insert into multitype values(1, '固定');
insert into multitype values(2, '非固定');
insert into series values(0, 'シリーズ不明');
insert into series values(1, 'QMA1');
insert into series values(2, 'QMA2');
insert into series values(3, 'QMA3');
insert into series values(4, 'QMA4');
insert into series values(5, 'QMA5');
insert into series values(6, 'QMA6');
insert into series values(7, 'QMA7');
insert into series values(8, 'QMA8');
insert into series values(9, 'QMA賢者の扉');
insert into series values(10, 'QMA天の学舎');
insert into series values(11, 'QMA暁の鐘');
insert into series values(12, 'QMAトーキョーグリモワール');
insert into stable values(0, '不安定');
insert into stable values(1, '安定');
    """)
    conn.commit()
    conn.close()
    print('done initialize')
