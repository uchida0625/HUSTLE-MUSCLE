from flask import Flask, render_template, request, redirect, url_for, session, g, flash, send_from_directory
import datetime
import sqlite3
import hashlib
import os
 
app = Flask(__name__)
 
# アプリケーションのルートディレクトリを取得
root_dir = os.path.dirname(os.path.abspath(__file__))
 
# データベースが存在するディレクトリに移動
os.chdir(root_dir)
 
# データベースに接続
conn = sqlite3.connect('exercise.db', check_same_thread=False)
# データベースに接続する際、絶対パスまたは相対パスを指定
db_path = os.path.join(root_dir, 'exercise.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
 
# アプリケーションがリクエストを処理する前にデータベースに接続
def get_db():
    db = sqlite3.connect('exercise.db', check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db
 
# アプリケーションがリクエストを処理した後にデータベース接続をクローズ
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
 
# アプリケーションがリクエストを処理する前にデータベースに接続
@app.before_request
def before_request():
    print("リクエスト処理の前: データベースに接続中")
    g.sqlite_db = get_db()
 
# アプリケーションがリクエストを処理した後にデータベース接続をクローズ
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
       
       
# セッションの秘密鍵を設定
app.secret_key = 'your_secret_key'
 
#インデックス画面
@app.route('/')
def index():
    return render_template('index.html')
 
#トップページの表示
@app.route('/top')
def top():
    user_id = session.get('user_id')
    if user_id is not None:
        return render_template('top.html', user_id=user_id)
    else:
        return render_template('top.html')
 
# ログアウトのルート
@app.route('/logout', methods=['POST'])
def logout():
    # ログアウトの処理
    session.pop('user_id', None)  # 例: セッションからユーザーIDを削除する
    return redirect(url_for('index'))  # ログアウト後に適切なページにリダイレクト
 
#アンケート
@app.route('/ank')
def ank():
    return render_template('ank.html')
 
#BMI計算ツール画面
@app.route('/keisan')
def keisan():
    return render_template('keisan.html')
 
#筋トレQ&A
@app.route('/qa')
def qa():
    return render_template('qa.html')

#筋トレ入門
@app.route('/training')
def training():
    return render_template('training.html')

#筋トレ動画
@app.route('/douga')
def douga():
    return render_template('douga.html')
 
#筋トレと栄養について
@app.route('/meal')
def meal():
    return render_template('meal.html') 
 
@app.route('/update_schedule/<day>', methods=['POST'])
def update_schedule(day):
    # SQLiteデータベース接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
 
    # フォームから送信されたデータを取得
    training_time = request.form.get(f'{day}_training_time')
    bmi = request.form.get(f'{day}_bmi')
 
    # データベース更新
    cursor.execute("UPDATE schedule SET training_time=?, bmi=? WHERE day=?", (training_time, bmi, day))
    conn.commit()
 
    # データベース接続終了
    conn.close()
 
    # リダイレクトまたは適切なレスポンスを返す
    return redirect(url_for('schedule'))
 
#動画ファイルのディレクトリ
VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'videos')
 
@app.route('/video/<filename>')
def video(filename):
    video_path = os.path.join(VIDEO_DIR, filename)
    return send_from_directory(VIDEO_DIR, filename, as_attachment=True)
 
#登録ボタンから登録画面へ
@app.route('/registry', methods=['GET'])
def show_registry_form():
    return render_template('register.html')
 
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
 
def authenticate_user(user_id, password):
    cursor = g.sqlite_db.cursor()
    cursor.execute("SELECT user_id, password FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
 
    if user_data:
        db_password_hash = user_data[1]
        input_password_hash = hash_password(password)
 
        if db_password_hash == input_password_hash:
            return user_data[0]  # ユーザーIDを返す
 
    return None
 

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # フォームから送信されたユーザーIDとパスワードを取得
        login_user_id = request.form.get('user_id')
        login_password = request.form.get('password')
 
        # ユーザーIDとパスワードが正しいかチェックする関数を呼び出す
        user_id = authenticate_user(login_user_id, login_password)
 
        if user_id:
            session['user_id'] = user_id
            print(f"ユーザーID: {user_id} でログインしました")  # ログに表示
            return redirect(url_for('top'))
        else:
            # ログイン失敗の場合
            flash('ユーザーIDまたはパスワードが正しくありません', 'error')
 
    # GETリクエスト時の処理（ログインフォームの表示）
    return render_template('index.html')
 
 
def get_user_id(username):
    conn = sqlite3.connect('exercise.db',  check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username=?", (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None
 
@app.route('/registry', methods=['GET', 'POST'])
def registry():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
 
        # フォームの検証などを行う
        # パスワードが確認用と一致するかを確認
        if password != confirm_password:
            print("Passwords do not match")
            flash('パスワードが一致しません', 'error')
            return render_template('register.html')
       
        print("Passwords match")
 
        try:
            # データベースに接続
            conn = sqlite3.connect('exercise.db', check_same_thread=False)
            cursor = conn.cursor()
 
            # テーブルが存在しない場合は作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password INTEGER NOT NULL
                )
            ''')
 
            hashed_password = hash_password(password)
 
            # データベースにユーザー情報を登録する SQL クエリを実行
            cursor.execute('''
                INSERT INTO users (username, password) VALUES (?, ?)
            ''', (username, hashed_password))
 
            # データベースの変更をコミット
            conn.commit()
 
            # 登録が成功した場合、登録完了ページにリダイレクト
            user_id = cursor.lastrowid  # 直近の挿入の自動増分IDを取得
            #flash(f'ユーザーID: {user_id} で登録が完了しました', 'success')
            return redirect(url_for('kanryou', user_id=user_id))
 
        except sqlite3.Error as e:
            # エラーハンドリング: エラーが発生した場合の処理を追加
            print("SQLiteエラー:", e)
            flash('データベースエラーが発生しました', 'error')
 
        finally:
            # 接続をクローズ
            conn.close()
 
    return render_template('register.html')
 
@app.route('/kanryou/<user_id>')
def kanryou(user_id):
    return render_template('kanryou.html', user_id=user_id)

# アンケート結果の保存
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        user_id = session.get('user_id')
        try:
            q1 = request.form['q1']
            q2 = request.form['q2']
            q3_neck = '首' in request.form.getlist('q3_首')
            q3_shoulder = '肩' in request.form.getlist('q3_肩')
            q3_elbow = '肘' in request.form.getlist('q3_肘')
            q3_waist = '腰' in request.form.getlist('q3_腰')
            q3_knee = '膝' in request.form.getlist('q3_膝')

            with sqlite3.connect('exercise.db') as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('INSERT INTO `ank` (user_id,q1,q2,q3_首,q3_肩,q3_肘,q3_腰,q3_膝) VALUES (?, ?, ?, ?, ?, ?, ?,?)',(user_id,q1, q2,q3_neck,q3_shoulder,q3_elbow,q3_waist,q3_knee))
                except:
                    cursor.execute('UPDATE `ank` SET q1 = ?,q2 = ?,q3_首 = ?,q3_肩 = ?,q3_肘 = ?,q3_腰 = ?,q3_膝 = ? WHERE user_id = ?',(q1, q2,q3_neck,q3_shoulder,q3_elbow,q3_waist,q3_knee,user_id))
            
            # トップページにリダイレクトする前にFlashメッセージを設定
            #flash('フォームが正しく送信されました\nスケジュールを確認してください', 'success')
        
            return redirect(url_for('top'))
        except Exception as e:
            return f'エラーが発生しました: {str(e)}'
    except:
        print("ユーザーIDの取得に失敗しました")

# アンケート結果を取得する関数
def get_survey_results(user_id):
    conn = sqlite3.connect('exercise.db',  check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT q1, q2 FROM ank WHERE user_id=?",(user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def determine_training_menu(q1, q2):
    if q1 == 1 and q2 == 30:
        return "30分メニュー1"
    elif q1 == 1 and q2 == 60:
        return "60分メニュー1"
    elif q1 == 1 and q2 == 90:
        return "90分メニュー1"
    elif q1 == 1 and q2 == 120:
        return "120分メニュー1"
    elif q1 == 2 and q2 == 30:
        return "30分メニュー2"
    elif q1 == 2 and q2 == 60:
        return "60分メニュー2"
    elif q1 == 2 and q2 == 90:
        return "90分メニュー2"
    elif q1 == 2 and q2 == 120:
        return "120分メニュー2"
    elif q1 == 3 and q2 == 30:
        return "30分メニュー3"
    elif q1 == 3 and q2 == 60:
        return "60分メニュー3"
    elif q1 == 3 and q2 == 90:
        return "90分メニュー3"
    elif q1 == 3 and q2 == 120:
        return "120分メニュー3"
    elif q1 == 4 and q2 == 30:
        return "30分メニュー4"
    elif q1 == 4 and q2 == 60:
        return "60分メニュー4"
    elif q1 == 4 and q2 == 90:
        return "90分メニュー4"
    elif q1 == 4 and q2 == 120:
        return "120分メニュー4"
    elif q1 == 5 and q2 == 30:
        return "30分メニュー5"
    elif q1 == 5 and q2 == 60:
        return "60分メニュー5"
    elif q1 == 5 and q2 == 90:
        return "90分メニュー5"
    else:
        return "120分メニュー5"
    
# スケジュールのルート
@app.route('/schedule')
def schedule():
    # セッションからログイン中のユーザーIDを取得
    user_id = session.get('user_id')

    if user_id is not None:
        survey_results = get_survey_results(user_id)
        q1, q2 = survey_results[0]
        training_menu = determine_training_menu(int(q1), int(q2))
        print(training_menu)
        work = get_training_menu(training_menu)[0]
        schedule_data = ["" if item is None else item for item in work]

        return render_template('schedule.html', schedule_data=schedule_data)
    else:
        # ユーザーがログインしていない場合の処理
        flash('ログインが必要です', 'error')
        return redirect(url_for('index'))
    
# トレーニングメニューを取得する関数（ユーザーIDごと）
def get_training_menu(menu_id):
    conn = sqlite3.connect('exercise.db',  check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT day1, day2, day3, day4, day5 FROM メニュー一覧 WHERE メニューID = ?", (menu_id,))
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    app.run(debug=True)
    
 