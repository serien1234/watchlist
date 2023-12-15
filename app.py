from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy # 导入扩展类
from flask import request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
from flask_login import LoginManager
from flask_login import login_required, current_user
from flask_login import login_required, logout_user
from flask_login import login_user
from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import random
import string

def generate_actor_id():
    # 获取当前时间的UNIX时间戳，并转换为36进制以缩短长度
    timestamp = base36_encode(int(dt.now().timestamp()))

    # 生成一个随机字母数字字符
    random_char = random.choice(string.ascii_letters + string.digits)

    # 将时间戳和随机字符组合成ID
    actor_id = f"{timestamp[:4]}{random_char}{timestamp[4:]}"
    return actor_id[:10]  # 确保ID不超过10个字符

def base36_encode(number):
    # 将数字转换为36进制的字符串
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = ''
    while number != 0:
        number, i = divmod(number, 36)
        base36 = '0123456789abcdefghijklmnopqrstuvwxyz'[i] + base36
    return base36
WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统， 使用三个斜线
    prefix = 'sqlite:///'
else: # 否则使用四个斜线
    prefix = 'sqlite:////'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
# 设置密钥
app.secret_key = '123456zaq'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
#MovieInfo 类对应 movie_info 表
class MovieInfo(db.Model):
    movie_id = db.Column(db.String(10), primary_key=True)
    movie_name = db.Column(db.String(20), nullable=False)
    release_date = db.Column(db.DateTime)
    country = db.Column(db.String(20))
    type = db.Column(db.String(10))
    year = db.Column(db.Integer, CheckConstraint('year>=1000 and year<=2100'))
    
#MoveBox 类对应 move_box 表
class MoveBox(db.Model):
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'), primary_key=True)
    box = db.Column(db.Float)
#ActorInfo 类对应 actor_info 表：
class ActorInfo(db.Model):
    actor_id = db.Column(db.String(10), primary_key=True)
    actor_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(20))
#MovieActorRelation 类对应 movie_actor_relation 表：
class MovieActorRelation(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'))
    actor_id = db.Column(db.String(10), db.ForeignKey('actor_info.actor_id'))
    relation_type = db.Column(db.String(20))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值
    def set_password(self, password): # 用来设置密码的方法， 接受密码作为参数
        self.password_hash = generate_password_hash(password) #将生成的密码保持到对应字段
    def validate_password(self, password): # 用于验证密码的方法， 接受密码作为参数
        return check_password_hash(self.password_hash, password)
# 返回布尔值

class Movie(db.Model): # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(240)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

import click
@app.cli.command()
@click.option('--username', prompt=True, help='The username usedto login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password) # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password) # 设置密码
        db.session.add(user)
    db.session.commit() # 提交数据库会话
    click.echo('Done.')

@app.cli.command() # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
# 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息

import click
from flask.cli import with_appcontext
import datetime

from app import db, MovieInfo, MoveBox, ActorInfo, MovieActorRelation
#输入数据
@app.cli.command()
@with_appcontext
def insertdata():
    """Insert data into the database."""

    # 创建数据库表
    db.create_all()

    # 插入电影信息
    movies_data = [
        {'movie_id': '1001', 'movie_name': '战狼2', 'release_date': datetime.datetime(2017, 7, 27), 'country': '中国', 'type': '战争', 'year': 2017},
        {'movie_id': '1002', 'movie_name': '哪吒之魔童降世', 'release_date': datetime.datetime(2019, 7, 26), 'country': '中国', 'type': '动画', 'year': 2019},
        {'movie_id': '1003', 'movie_name': '流浪地球', 'release_date': datetime.datetime(2019, 2, 5), 'country': '中国', 'type': '科幻', 'year': 2019},
        {'movie_id': '1004', 'movie_name': '复仇者联盟4', 'release_date': datetime.datetime(2019, 4, 24), 'country': '美国', 'type': '科幻', 'year': 2019},
        {'movie_id': '1005', 'movie_name': '红海行动', 'release_date': datetime.datetime(2018, 2, 16), 'country': '中国', 'type': '战争', 'year': 2018},
        {'movie_id': '1006', 'movie_name': '唐人街探案2', 'release_date': datetime.datetime(2018, 2, 16), 'country': '中国', 'type': '喜剧', 'year': 2018},
        {'movie_id': '1007', 'movie_name': '我不是药神', 'release_date': datetime.datetime(2018, 7, 5), 'country': '中国', 'type': '喜剧', 'year': 2018},
        {'movie_id': '1008', 'movie_name': '中国机长', 'release_date': datetime.datetime(2019, 9, 30), 'country': '中国', 'type': '剧情', 'year': 2019},
        {'movie_id': '1009', 'movie_name': '速度与激情8', 'release_date': datetime.datetime(2017, 4, 14), 'country': '美国', 'type': '动作', 'year': 2017},
        {'movie_id': '1010', 'movie_name': '西虹市首富', 'release_date': datetime.datetime(2018, 7, 27), 'country': '中国', 'type': '喜剧', 'year': 2018},
        {'movie_id': '1011', 'movie_name': '复仇者联盟3', 'release_date': datetime.datetime(2018, 5, 11), 'country': '美国', 'type': '科幻', 'year': 2018},
        {'movie_id': '1012', 'movie_name': '捉妖记2', 'release_date': datetime.datetime(2018, 2, 16), 'country': '中国', 'type': '喜剧', 'year': 2018},
        {'movie_id': '1013', 'movie_name': '八佰', 'release_date': datetime.datetime(2020, 8, 21), 'country': '中国', 'type': '战争', 'year': 2020},
        {'movie_id': '1014', 'movie_name': '姜子牙', 'release_date': datetime.datetime(2020, 10, 1), 'country': '中国', 'type': '动画', 'year': 2020},
        {'movie_id': '1015', 'movie_name': '我和我的家乡', 'release_date': datetime.datetime(2020, 10, 1), 'country': '中国', 'type': '剧情', 'year': 2020},
        {'movie_id': '1016', 'movie_name': '你好，李焕英', 'release_date': datetime.datetime(2021, 2, 12), 'country': '中国', 'type': '喜剧', 'year': 2021},
        {'movie_id': '1017', 'movie_name': '长津湖', 'release_date': datetime.datetime(2021, 9, 30), 'country': '中国', 'type': '战争', 'year': 2021},
        {'movie_id': '1018', 'movie_name': '速度与激情9', 'release_date': datetime.datetime(2021, 5, 21), 'country': '中国', 'type': '动作', 'year': 2021},
        # 继续插入其他电影数据...
    ]

    for data in movies_data:
        movie = MovieInfo(**data)
        db.session.add(movie)

    # 插入票房数据
    move_box_data = [
        {'movie_id': '1001', 'box': 56.84},
        {'movie_id': '1002', 'box': 50.15},
        {'movie_id': '1003', 'box': 46.86},
        {'movie_id': '1004', 'box': 42.5},
        {'movie_id': '1005', 'box': 36.5},
        {'movie_id': '1006', 'box': 33.97},
        {'movie_id': '1007', 'box': 31},
        {'movie_id': '1008', 'box': 29.12},
        {'movie_id': '1009', 'box': 26.7},
        {'movie_id': '1010', 'box': 25.47},
        {'movie_id': '1011', 'box': 23.9},
        {'movie_id': '1012', 'box': 22.37},
        {'movie_id': '1013', 'box': 30.10},
        {'movie_id': '1014', 'box': 16.02},
        {'movie_id': '1015', 'box': 28.29},
        {'movie_id': '1016', 'box': 54.13},
        {'movie_id': '1017', 'box': 53.48},
        {'movie_id': '1018', 'box': 13.92},
        # 继续插入其他票房数据...
    ]

    for data in move_box_data:
        box = MoveBox(**data)
        db.session.add(box)

    # 插入演员信息
    actors_data = [
        {'actor_id': '2001', 'actor_name': '吴京', 'gender': '男', 'country': '中国'},
        {'actor_id': '2002', 'actor_name': '饺子', 'gender': '男', 'country': '中国'},
        {'actor_id': '2003', 'actor_name': '屈楚萧', 'gender': '男', 'country': '中国'},
        {'actor_id': '2004', 'actor_name': '郭帆', 'gender': '男', 'country': '中国'},
        {'actor_id': '2005', 'actor_name': '乔罗素', 'gender': '男', 'country': '美国'},
        {'actor_id': '2006', 'actor_name': '小罗伯特·唐尼', 'gender': '男', 'country': '美国'},
        {'actor_id': '2007', 'actor_name': '克里斯·埃文斯', 'gender': '男', 'country': '美国'},
        {'actor_id': '2008', 'actor_name': '林超贤', 'gender': '男', 'country': '中国'},
        {'actor_id': '2009', 'actor_name': '张译', 'gender': '男', 'country': '中国'},
        {'actor_id': '2010', 'actor_name': '黄景瑜', 'gender': '男', 'country': '中国'},
        {'actor_id': '2011', 'actor_name': '陈思诚', 'gender': '男', 'country': '中国'},
        {'actor_id': '2012', 'actor_name': '王宝强', 'gender': '男', 'country': '中国'},
        {'actor_id': '2013', 'actor_name': '刘昊然', 'gender': '男', 'country': '中国'},
        {'actor_id': '2014', 'actor_name': '文牧野', 'gender': '男', 'country': '中国'},
        {'actor_id': '2015', 'actor_name': '徐峥', 'gender': '男', 'country': '中国'},
        {'actor_id': '2016', 'actor_name': '刘伟强', 'gender': '男', 'country': '中国'},
        {'actor_id': '2017', 'actor_name': '张涵予', 'gender': '男', 'country': '中国'},
        {'actor_id': '2018', 'actor_name': 'F·加里·格雷', 'gender': '男', 'country': '美国'},
        {'actor_id': '2019', 'actor_name': '范·迪塞尔', 'gender': '男', 'country': '美国'},
        {'actor_id': '2020', 'actor_name': '杰森·斯坦森', 'gender': '男', 'country': '美国'},
        {'actor_id': '2021', 'actor_name': '闫非', 'gender': '男', 'country': '中国'},
        {'actor_id': '2022', 'actor_name': '沈腾', 'gender': '男', 'country': '中国'},
        {'actor_id': '2023', 'actor_name': '安东尼·罗素', 'gender': '男', 'country': '美国'},
        {'actor_id': '2024', 'actor_name': '克里斯·海姆斯沃斯', 'gender': '男', 'country': '美国'},
        {'actor_id': '2025', 'actor_name': '许诚毅', 'gender': '男', 'country': '中国'},
        {'actor_id': '2026', 'actor_name': '梁朝伟', 'gender': '男', 'country': '中国'},
        {'actor_id': '2027', 'actor_name': '白百何', 'gender': '女', 'country': '中国'},
        {'actor_id': '2028', 'actor_name': '井柏然', 'gender': '男', 'country': '中国'},
        {'actor_id': '2029', 'actor_name': '管虎', 'gender': '男', 'country': '中国'},
        {'actor_id': '2030', 'actor_name': '王千源', 'gender': '男', 'country': '中国'},
        {'actor_id': '2031', 'actor_name': '姜武', 'gender': '男', 'country': '中国'},
        {'actor_id': '2032', 'actor_name': '宁浩', 'gender': '男', 'country': '中国'},
        {'actor_id': '2033', 'actor_name': '葛优', 'gender': '男', 'country': '中国'},
        {'actor_id': '2034', 'actor_name': '范伟', 'gender': '男', 'country': '中国'},
        {'actor_id': '2035', 'actor_name': '贾玲', 'gender': '女', 'country': '中国'},
        {'actor_id': '2036', 'actor_name': '张小斐', 'gender': '女', 'country': '中国'},
        {'actor_id': '2037', 'actor_name': '陈凯歌', 'gender': '男', 'country': '中国'},
        {'actor_id': '2038', 'actor_name': '徐克', 'gender': '男', 'country': '中国'},
        {'actor_id': '2039', 'actor_name': '易烊千玺', 'gender': '男', 'country': '中国'},
        {'actor_id': '2040', 'actor_name': '林诣彬', 'gender': '男', 'country': '美国'},
        {'actor_id': '2041', 'actor_name': '米歇尔·罗德里格兹', 'gender': '女', 'country': '美国'},
        # 继续插入其他演员数据...
    ]
    for data in actors_data:
        actor = ActorInfo(**data)
        db.session.add(actor)

    # 插入电影和演员的关系
    movie_actor_relation_data = [
        {'id': '1', 'movie_id': '1001', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '2', 'movie_id': '1001', 'actor_id': '2001', 'relation_type': '导演'},
        {'id': '3', 'movie_id': '1002', 'actor_id': '2002', 'relation_type': '导演'},
        {'id': '4', 'movie_id': '1003', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '5', 'movie_id': '1003', 'actor_id': '2003', 'relation_type': '主演'},
        {'id': '6', 'movie_id': '1003', 'actor_id': '2004', 'relation_type': '导演'},
        {'id': '7', 'movie_id': '1004', 'actor_id': '2005', 'relation_type': '导演'},
        {'id': '8', 'movie_id': '1004', 'actor_id': '2006', 'relation_type': '主演'},
        {'id': '9', 'movie_id': '1004', 'actor_id': '2007', 'relation_type': '主演'},
        {'id': '10', 'movie_id': '1005', 'actor_id': '2008', 'relation_type': '导演'},
        {'id': '11', 'movie_id': '1005', 'actor_id': '2009', 'relation_type': '主演'},
        {'id': '12', 'movie_id': '1005', 'actor_id': '2010', 'relation_type': '主演'},
        {'id': '13', 'movie_id': '1006', 'actor_id': '2011', 'relation_type': '导演'},
        {'id': '14', 'movie_id': '1006', 'actor_id': '2012', 'relation_type': '主演'},
        {'id': '15', 'movie_id': '1006', 'actor_id': '2013', 'relation_type': '主演'},
        {'id': '16', 'movie_id': '1007', 'actor_id': '2014', 'relation_type': '导演'},
        {'id': '17', 'movie_id': '1007', 'actor_id': '2015', 'relation_type': '主演'},
        {'id': '18', 'movie_id': '1008', 'actor_id': '2016', 'relation_type': '导演'},
        {'id': '19', 'movie_id': '1008', 'actor_id': '2017', 'relation_type': '主演'},
        {'id': '20', 'movie_id': '1009', 'actor_id': '2018', 'relation_type': '导演'},
        {'id': '21', 'movie_id': '1009', 'actor_id': '2019', 'relation_type': '主演'},
        {'id': '22', 'movie_id': '1009', 'actor_id': '2020', 'relation_type': '主演'},
        {'id': '23', 'movie_id': '1010', 'actor_id': '2021', 'relation_type': '导演'},
        {'id': '24', 'movie_id': '1010', 'actor_id': '2022', 'relation_type': '主演'},
        {'id': '25', 'movie_id': '1011', 'actor_id': '2023', 'relation_type': '导演'},
        {'id': '26', 'movie_id': '1011', 'actor_id': '2006', 'relation_type': '主演'},
        {'id': '27', 'movie_id': '1011', 'actor_id': '2024', 'relation_type': '主演'},
        {'id': '28', 'movie_id': '1012', 'actor_id': '2025', 'relation_type': '导演'},
        {'id': '29', 'movie_id': '1012', 'actor_id': '2026', 'relation_type': '主演'},
        {'id': '30', 'movie_id': '1012', 'actor_id': '2027', 'relation_type': '主演'},
        {'id': '31', 'movie_id': '1012', 'actor_id': '2028', 'relation_type': '主演'},
        {'id': '32', 'movie_id': '1013', 'actor_id': '2029', 'relation_type': '导演'},
        {'id': '33', 'movie_id': '1013', 'actor_id': '2030', 'relation_type': '主演'},
        {'id': '34', 'movie_id': '1013', 'actor_id': '2009', 'relation_type': '主演'},
        {'id': '35', 'movie_id': '1013', 'actor_id': '2031', 'relation_type': '主演'},
        {'id': '36', 'movie_id': '1015', 'actor_id': '2032', 'relation_type': '导演'},
        {'id': '37', 'movie_id': '1015', 'actor_id': '2015', 'relation_type': '导演'},
        {'id': '38', 'movie_id': '1015', 'actor_id': '2011', 'relation_type': '导演'},
        {'id': '39', 'movie_id': '1015', 'actor_id': '2015', 'relation_type': '主演'},
        {'id': '40', 'movie_id': '1015', 'actor_id': '2033', 'relation_type': '主演'},
        {'id': '41', 'movie_id': '1015', 'actor_id': '2034', 'relation_type': '主演'},
        {'id': '42', 'movie_id': '1016', 'actor_id': '2035', 'relation_type': '导演'},
        {'id': '43', 'movie_id': '1016', 'actor_id': '2035', 'relation_type': '主演'},
        {'id': '44', 'movie_id': '1016', 'actor_id': '2036', 'relation_type': '主演'},
        {'id': '45', 'movie_id': '1016', 'actor_id': '2022', 'relation_type': '主演'},
        {'id': '46', 'movie_id': '1017', 'actor_id': '2037', 'relation_type': '导演'},
        {'id': '47', 'movie_id': '1017', 'actor_id': '2038', 'relation_type': '导演'},
        {'id': '48', 'movie_id': '1017', 'actor_id': '2008', 'relation_type': '导演'},
        {'id': '49', 'movie_id': '1017', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '50', 'movie_id': '1017', 'actor_id': '2039', 'relation_type': '主演'},
        {'id': '51', 'movie_id': '1018', 'actor_id': '2040', 'relation_type': '导演'},
        {'id': '52', 'movie_id': '1018', 'actor_id': '2019', 'relation_type': '主演'},
        {'id': '53', 'movie_id': '1018', 'actor_id': '2041', 'relation_type': '主演'},
    ]
    for data in movie_actor_relation_data:
        relation = MovieActorRelation(**data)
        db.session.add(relation)

    # 提交更改到数据库
    db.session.commit()

    click.echo('Data inserted successfully.')

@app.context_processor
def inject_user(): # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user) # 需要返回字典， 等同于return {'user': user}

@app.errorhandler(404) # 传入要处理的错误代码
def page_not_found(e): # 接受异常对象作为参数
    return render_template('404.html'), 404 # 返回模板和状态码


login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数， 接受用户 ID 作为参数
    user = User.query.get(int(user_id)) # 用 ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 登入用户
            flash('Login success.')
            return redirect(url_for('index')) # 重定向到主页
        flash('Invalid username or password.') # 如果验证失败， 显示错误消息
        return redirect(url_for('login')) # 重定向回登录页面
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user() # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index')) # 重定向回首页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
        if not current_user.is_authenticated: # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向回主页
        # 获取表单数据
        movie_name = request.form.get('movie_name') # 传入表单对应输入字段的name 值
        year = request.form.get('year')
        # 验证数据
        if not movie_name or not year or len(year) > 4 or len(movie_name)> 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = MovieInfo(movie_name=movie_name, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示
        return redirect(url_for('index')) # 重定向回主页
    user = User.query.first()
    movies = MovieInfo.query.all()
    return render_template('index.html', user=user, movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required # 用于视图保护， 后面会详细介绍
def edit(movie_id):
    movie = MovieInfo.query.get_or_404(movie_id)
    if request.method == 'POST': # 处理编辑表单的提交请求
        movie_name = request.form['movie_name']
        year = request.form['year']
        if not movie_name or not year or len(year) > 4 or len(movie_name)> 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        # 重定向回对应的编辑页面
        movie.movie_name = movie_name # 更新标题
        movie.year = year # 更新年份
        db.session.commit() # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index')) # 重定向回主页
    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST']) #限定只接受 POST 请求
@login_required # 登录保护
def delete(movie_id):
    movie = MovieInfo.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie) # 删除对应的记录
    db.session.commit() # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页


from datetime import datetime as dt
@app.route('/addmovie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.method == 'POST':
        # 获取电影基本信息
        movie_id = request.form.get('movie_id')
        movie_name = request.form.get('movie_name')
        release_date = request.form.get('release_date')
        country = request.form.get('country')
        movie_type = request.form.get('type')
        year = request.form.get('year')
        box_office = request.form.get('box_office')
        director_name = request.form.get('director_name')  # 获取导演姓名
        lead_actor_names = request.form.get('lead_actor_names')  # 获取主演姓名

        # 数据验证
        if not all([movie_id, movie_name, release_date, country, movie_type, year, box_office, director_name, lead_actor_names]):
            flash('所有字段都是必填的.')
            return redirect(url_for('add_movie'))

        # 转换日期格式
        try:
            release_date = dt.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            flash('无效的日期格式.')
            return redirect(url_for('add_movie'))
        # 检查电影ID是否已存在
        existing_movie_id = MovieInfo.query.filter_by(movie_id=movie_id).first()
        if existing_movie_id:
            flash('电影ID已存在.')
            return redirect(url_for('add_movie'))
        # 检查电影名称是否已存在
        existing_movie = MovieInfo.query.filter_by(movie_name=movie_name).first()
        if existing_movie:
            flash('电影名称已存在.')
            return redirect(url_for('add_movie'))
        # 创建新电影对象
        new_movie = MovieInfo(
            movie_id=movie_id,
            movie_name=movie_name,
            release_date=release_date,
            country=country,
            type=movie_type,
            year=int(year)
        )
        db.session.add(new_movie)

        # 添加电影票房信息
        new_box = MoveBox(
            movie_id=movie_id,
            box=float(box_office)
        )
        db.session.add(new_box)

        # 添加导演信息
        director = ActorInfo.query.filter_by(actor_name=director_name).first()
        if not director:
            # 重定向到添加演员信息的界面
            return redirect(url_for('add_actor', movie_id=movie_id, actor_name=director_name))

        new_director_relation = MovieActorRelation(
            id=generate_relation_id(),
            movie_id=movie_id,
            actor_id=director.actor_id,
            relation_type='导演'
        )
        db.session.add(new_director_relation)

        # 添加主演信息
        for actor_name in lead_actor_names.split(','):
            actor = ActorInfo.query.filter_by(actor_name=actor_name.strip()).first()
            if not actor:
                # 重定向到添加演员信息的界面
                return redirect(url_for('add_actor', movie_id=movie_id, actor_name=actor_name.strip()))

            new_actor_relation = MovieActorRelation(
                id=generate_relation_id(),
                movie_id=movie_id,
                actor_id=actor.actor_id,
                relation_type='主演'
            )
            db.session.add(new_actor_relation)

        db.session.commit()
        flash('电影及演员信息添加成功.')
        return redirect(url_for('index'))

    return render_template('addmovie.html')

def add_or_get_actor(actor_name, relation_type, movie_id):
    actor = ActorInfo.query.filter_by(actor_name=actor_name).first()
    if not actor:
        actor_id = generate_actor_id()
        actor = ActorInfo(actor_id=actor_id, actor_name=actor_name)
        db.session.add(actor)
    new_relation = MovieActorRelation(
        id=generate_relation_id(),  # 新函数用于生成关系ID
        movie_id=movie_id,
        actor_id=actor.actor_id,
        relation_type=relation_type
    )
    return new_relation

def generate_relation_id():
    # 实现一个函数来生成唯一的关系ID
    # 示例：使用时间戳和随机数
    timestamp = dt.now().strftime('%Y%m%d%H%M%S')
    random_number = random.randint(100, 999)
    return f"rel_{timestamp}_{random_number}"

@app.route('/addactor', methods=['GET', 'POST'])
def add_actor():
    movie_id = request.args.get('movie_id')
    actor_name = request.args.get('actor_name')

    if request.method == 'POST':
        actor_name = request.form.get('actor_name')
        gender = request.form.get('gender')
        country = request.form.get('country')

        # 生成一个新的 actor_id，或者根据实际情况修改
        actor_id = generate_actor_id()  # 需要一个函数来生成唯一的 actor_id

        # 数据验证
        if not all([actor_name, gender, country]):
            flash('所有字段都是必填的.')
            return redirect(url_for('add_actor', movie_id=movie_id, actor_name=actor_name))
        # 检查演员信息是否已存在
        existing_actor = ActorInfo.query.filter_by(actor_name=actor_name, gender=gender, country=country).first()
        if existing_actor:
            flash('相同的演员信息已存在.')
            return redirect(url_for('add_actor', movie_id=movie_id, actor_name=actor_name))
        # 创建新演员对象
        new_actor = ActorInfo(
            actor_id=actor_id,
            actor_name=actor_name,
            gender=gender,
            country=country
        )
        db.session.add(new_actor)
        db.session.commit()
        flash('演员信息添加成功.')

        # 重定向回添加电影页面
        return redirect(url_for('add_movie', movie_id=movie_id))

    return render_template('addactor.html', movie_id=movie_id, actor_name=actor_name)




@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_results')
def search_results():
    query_type = request.args.get('type')
    query = request.args.get('query')

    if query_type == 'movie':
        movies = MovieInfo.query.filter(MovieInfo.movie_name.like(f'%{query}%')).all()
        results = []
        for movie in movies:
            # 获取与电影相关的演员及其关系信息
            relations = MovieActorRelation.query.filter_by(movie_id=movie.movie_id).all()
            actor_relations = []
            for relation in relations:
                actor = ActorInfo.query.get(relation.actor_id)
                actor_relations.append({'actor': actor, 'relation_type': relation.relation_type})
            results.append({'movie': movie, 'relations': actor_relations})
    elif query_type == 'actor':
        actors = ActorInfo.query.filter(ActorInfo.actor_name.like(f'%{query}%')).all()
        results = []
        for actor in actors:
            # 获取演员参演的电影及其关系信息
            relations = MovieActorRelation.query.filter_by(actor_id=actor.actor_id).all()
            movie_relations = []
            for relation in relations:
                movie = MovieInfo.query.get(relation.movie_id)
                movie_relations.append({'movie': movie, 'relation_type': relation.relation_type})
            results.append({'actor': actor, 'relations': movie_relations})
    else:
        results = []

    return render_template('search_results.html', results=results, type=query_type)


@app.route('/box_office', methods=['GET', 'POST'])
def box_office():
    movies = db.session.query(
        MovieInfo.movie_name,
        MoveBox.box
    ).join(MoveBox, MovieInfo.movie_id == MoveBox.movie_id).all()

    total_box = sum(movie.box for movie in movies)
    avg_box = total_box / len(movies) if movies else 0
    top_movie = max(movies, key=lambda movie: movie.box) if movies else None
    # 获取每个年份的平均票房
    year_avg_box = db.session.query(
        MovieInfo.year,
        db.func.avg(MoveBox.box).label('avg_box')
    ).join(MoveBox, MovieInfo.movie_id == MoveBox.movie_id).group_by(MovieInfo.year).all()
    search_results = None
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        name = request.form.get('name')

        if search_type == 'director':
            search_results = db.session.query(
                MovieInfo.movie_name, MoveBox.box
            ).join(MoveBox).join(MovieActorRelation).join(ActorInfo).filter(
                MovieActorRelation.relation_type == '导演',
                ActorInfo.actor_name == name
            ).all()
        elif search_type == 'actor':
            search_results = db.session.query(
                MovieInfo.movie_name, MoveBox.box
            ).join(MoveBox).join(MovieActorRelation).join(ActorInfo).filter(
                MovieActorRelation.relation_type == '主演',
                ActorInfo.actor_name == name
            ).all()
    return render_template('box_office.html', movies=movies, total_box=total_box, avg_box=avg_box, top_movie=top_movie, year_avg_box=year_avg_box,search_results=search_results)
    


@app.route('/box_office_prediction', methods=['GET', 'POST'])
def box_office_prediction():
    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        release_date = request.form.get('release_date')
        lead_actor = request.form.get('lead_actor')
        director = request.form.get('director')
        movie_type = request.form.get('movie_type')

        # 根据输入的信息计算预测票房
        actor_avg_box = calculate_actor_avg_box(lead_actor)
        director_avg_box = calculate_director_avg_box(director)
        year_avg_box = calculate_year_avg_box(release_date)
        type_avg_box = calculate_type_avg_box(movie_type)

        # 假设预测票房是这些均值的组合
        predicted_box_office = (actor_avg_box + director_avg_box + year_avg_box + type_avg_box) / 4

        return render_template('box_office_prediction_result.html',
                               predicted_box_office=predicted_box_office,
                               actor_avg_box=actor_avg_box,
                               director_avg_box=director_avg_box,
                               year_avg_box=year_avg_box,
                               type_avg_box=type_avg_box)

    return render_template('box_office_prediction.html')

    # 实现根据演员名称计算其主演电影的平均票房
def calculate_actor_avg_box(actor_name):
    result = db.session.query(db.func.avg(MoveBox.box)).join(
        MovieActorRelation, MoveBox.movie_id == MovieActorRelation.movie_id
    ).join(
        ActorInfo, MovieActorRelation.actor_id == ActorInfo.actor_id
    ).filter(
        ActorInfo.actor_name == actor_name,
        MovieActorRelation.relation_type == '主演'
    ).scalar()
    return result if result else 0

    # 实现根据导演名称计算其导演电影的平均票房

def calculate_director_avg_box(director_name):
    result = db.session.query(db.func.avg(MoveBox.box)).join(
        MovieActorRelation, MoveBox.movie_id == MovieActorRelation.movie_id
    ).join(
        ActorInfo, MovieActorRelation.actor_id == ActorInfo.actor_id
    ).filter(
        ActorInfo.actor_name == director_name,
        MovieActorRelation.relation_type == '导演'
    ).scalar()
    return result if result else 0

    # 实现根据上映年份计算当年电影的平均票房


def calculate_type_avg_box(movie_type):
    result = db.session.query(db.func.avg(MoveBox.box)).join(
        MovieInfo, MoveBox.movie_id == MovieInfo.movie_id
    ).filter(
        MovieInfo.type == movie_type
    ).scalar()
    return result if result else 0

def calculate_year_avg_box(release_date_str):
    try:
        release_date = dt.strptime(release_date_str, '%Y-%m-%d')  # 转换为 datetime 对象
        year = release_date.year
        result = db.session.query(db.func.avg(MoveBox.box)).join(
            MovieInfo, MoveBox.movie_id == MovieInfo.movie_id
        ).filter(
            db.func.extract('year', MovieInfo.release_date) == year
        ).scalar()
    except ValueError:
        # 如果日期格式不正确，可以返回一个默认值或抛出错误
        return 0

    # 计算该年份的平均票房
    result = db.session.query(db.func.avg(MoveBox.box)).join(
        MovieInfo, MoveBox.movie_id == MovieInfo.movie_id
    ).filter(
        db.func.extract('year', MovieInfo.release_date) == year
    ).scalar()
    return result if result else 0
