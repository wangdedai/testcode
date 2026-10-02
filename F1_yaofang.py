# # !/usr/bin/env python
# # -*- coding: utf-8 -*-
# import roslib
# import rospy
# import actionlib
# from actionlib_msgs.msg import *
# from geometry_msgs.msg import Pose, Point, Quaternion, Twist
# from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
# from tf.transformations import quaternion_from_euler
# from visualization_msgs.msg import Marker
# from math import radians, pi
# from std_msgs.msg import Int32
# from std_msgs.msg import Int32MultiArray
# from std_srvs.srv import Empty
# import os
# import random
#
#
# class MoveBaseSquare():
#     def __init__(self):
#         rospy.init_node('nav_pharmacy', anonymous=False)
#         rospy.on_shutdown(self.shutdown)
#
#         # 角度和路径点初始化（保持不变）
#         quaternions = list()
#         euler_angles = (pi / 2, pi / 2, 5 * pi / 9, -5 * pi / 9, -pi / 2, -pi / 2, -pi / 2, 0, -pi, 0)
#         for angle in euler_angles:
#             q_angle = quaternion_from_euler(0, 0, angle, axes='sxyz')
#             q = Quaternion(*q_angle)
#             quaternions.append(q)
#
#         waypoints = list()
#         waypoints.append(Pose(Point(1.375, 2.215, 0), quaternions[0]))  # //C
#         waypoints.append(Pose(Point(0.590, 2.645, 0), quaternions[1]))  # //A
#         waypoints.append(Pose(Point(1.375, 3.100, 0), quaternions[2]))  # //B
#         waypoints.append(Pose(Point(-0.900, 0.805, 0), quaternions[3]))  # //4
#         waypoints.append(Pose(Point(-1.700, 1.232, 0), quaternions[4]))  # //3
#         waypoints.append(Pose(Point(-0.877, 1.775, 0), quaternions[5]))  # //2
#         waypoints.append(Pose(Point(-1.800, 2.281, 0), quaternions[6]))  # //1
#         waypoints.append(Pose(Point(-0.035, -0.184, 0), quaternions[7]))  # 起点
#         waypoints.append(Pose(Point(-0.690, 3.900, 0), quaternions[8]))  # 答题区(识别板2)
#         waypoints.append(Pose(Point(0.840, 0.040, 0), quaternions[9]))  # 识别板1
#
#         # 状态变量初始化
#         self.count = 9
#         self.windows_ABC = 0
#         self.windows_A = 1
#         self.windows_B = 1
#         self.windows_C = 1
#         self.windows_1234 = 3
#
#         # ROS发布者和订阅者
#         self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
#         self.cam_sub = rospy.Subscriber('/cam_return', Int32MultiArray, self.detect_result, queue_size=10)
#         self.ram_result = [1, 1, 1, 3, 4]
#         rospy.sleep(1)
#
#         # 导航相关初始化
#         self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
#         rospy.loginfo("Waiting for move_base action server...")
#         self.move_base.wait_for_server(rospy.Duration(60))
#         rospy.wait_for_service('/move_base/clear_costmaps')
#         self.clear_costmaps_service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
#         rospy.loginfo("Starting navigation...")
#
#         # 语音文件路径定义（使用format()方法）
#         self.audio_path = '/home/EPRobot/robot_ws/src/pharmacy_pkg/yuyinwenjian/'
#
#         # 取样本窗口的语音文件
#         self.wav_get_A = '{}{}'.format(self.audio_path, '取到A窗口中的样本.wav')
#         self.wav_get_B = '{}{}'.format(self.audio_path, '取到B窗口中的样本.wav')
#         self.wav_get_C = '{}{}'.format(self.audio_path, '取到C窗口中的样本.wav')
#         self.wav_get_AB = '{}{}'.format(self.audio_path, '取到A、B窗口中的样本.wav')
#         self.wav_get_AC = '{}{}'.format(self.audio_path, '取到C、A窗口中的样本.wav')
#         self.wav_get_BC = '{}{}'.format(self.audio_path, '取到C、B窗口中的样本.wav')
#         self.wav_get_ABC = '{}{}'.format(self.audio_path, '取到C、A、B窗口中的样本.wav')
#
#         # 样本类型语音文件
#         self.wav_venous_blood = '{}{}'.format(self.audio_path, '静脉血样本.wav')
#         self.wav_saliva = '{}{}'.format(self.audio_path, '唾液样本.wav')
#         self.wav_tissue = '{}{}'.format(self.audio_path, '组织样本.wav')
#         self.wav_plasma = '{}{}'.format(self.audio_path, '血浆样本.wav')
#
#         # 样本数量语音文件
#         self.wav_count_1 = '{}{}'.format(self.audio_path, '样本数为1.wav')
#         self.wav_count_2 = '{}{}'.format(self.audio_path, '样本数为2.wav')
#         self.wav_count_3 = '{}{}'.format(self.audio_path, '样本数为3.wav')
#
#         # 到达窗口语音文件
#         self.wav_arrive_hormone = '{}{}'.format(self.audio_path, '到达激素检验窗口.wav')
#         self.wav_arrive_immune = '{}{}'.format(self.audio_path, '到达免疫检测窗口.wav')
#         self.wav_arrive_humoral = '{}{}'.format(self.audio_path, '到达体液检验窗口.wav')
#         self.wav_arrive_blood = '{}{}'.format(self.audio_path, '到达血常规检验窗口.wav')
#
#         # 主循环
#         while not rospy.is_shutdown():
#             # 状态机逻辑（保持不变）
#             if self.count == 9:  # 从起点到识别区
#                 rospy.loginfo("从起点到识别区")
#                 goal = MoveBaseGoal()
#                 goal.target_pose.header.frame_id = 'map'
#                 goal.target_pose.header.stamp = rospy.Time.now()
#                 goal.target_pose.pose = waypoints[9]
#                 if self.move(goal) == True:
#                     rospy.loginfo("到达识别区。。。。。。。。")
#                     self.count = 10
#                     self.clear_costmaps_service()
#                     rospy.sleep(5)
#
#             elif self.count == 10:  # 从起点到配药区
#                 rospy.loginfo('10101010101010')
#                 goal = MoveBaseGoal()
#                 goal.target_pose.header.frame_id = 'map'
#                 goal.target_pose.header.stamp = rospy.Time.now()
#
#                 if self.windows_C == 1:  # 是否去C
#                     goal.target_pose.pose = waypoints[0]
#                     if self.move(goal) == True:
#                         rospy.loginfo("取到C窗口中的")
#                         os.system('play {}'.format(self.wav_get_C))
#                         self.count = 11
#                         self.clear_costmaps_service()
#                         rospy.sleep(1)
#
#                 if self.windows_A == 1:  # 是否去A
#                     goal.target_pose.pose = waypoints[1]
#                     if self.move(goal) == True:
#                         rospy.loginfo("取到A窗口中的")
#                         os.system('play {}'.format(self.wav_get_A))
#                         self.count = 11
#                         self.clear_costmaps_service()
#                         rospy.sleep(1)
#
#                 if self.windows_B == 1:  # 是否去B
#                     goal.target_pose.pose = waypoints[2]
#                     if self.move(goal) == True:
#                         rospy.loginfo("取到B窗口中的")
#                         os.system('play {}'.format(self.wav_get_B))
#                         self.count = 11
#                         self.clear_costmaps_service()
#                         rospy.sleep(1)
#
#                 self.count = 11
#
#                 # 播报样本类型
#                 if self.windows_1234 == 3:  # 4(激素检验窗口)
#                     rospy.loginfo("血浆样本")
#                     os.system('play {}'.format(self.wav_plasma))
#                 elif self.windows_1234 == 4:  # 3(免疫检测窗口)
#                     rospy.loginfo("组织样本")
#                     os.system('play {}'.format(self.wav_tissue))
#                 elif self.windows_1234 == 5:  # 2(体液窗口)
#                     rospy.loginfo("唾液样本")
#                     os.system('play {}'.format(self.wav_saliva))
#                 elif self.windows_1234 == 6:  # 1(血常规窗口)
#                     rospy.loginfo("静脉血样本")
#                     os.system('play {}'.format(self.wav_venous_blood))
#
#             elif self.count == 11:  # 从配药区到答题区
#                 rospy.loginfo("从配药区到答题区路上")
#                 goal = MoveBaseGoal()
#                 goal.target_pose.header.frame_id = 'map'
#                 goal.target_pose.header.stamp = rospy.Time.now()
#                 goal.target_pose.pose = waypoints[8]
#                 if self.move(goal) == True:
#                     rospy.loginfo("到达识别板2。。。。。。。。")
#                     self.count = 12
#                     self.clear_costmaps_service()
#                     rospy.loginfo("化验区无空闲，等待中")
#                     rospy.sleep(1)
#
#             elif self.count == 12:  # 从答题区到数字区
#                 rospy.loginfo("从答题区到数字区路上")
#                 goal = MoveBaseGoal()
#                 goal.target_pose.header.frame_id = 'map'
#                 goal.target_pose.header.stamp = rospy.Time.now()
#                 goal.target_pose.pose = waypoints[(6 - self.windows_1234)]
#                 if self.move(goal) == True:
#                     rospy.loginfo("到达数字区。。。。。。。。")
#                     self.count = 9
#                     self.clear_costmaps_service()
#                     rospy.sleep(1)
#
#                     # 播报到达位置
#                     if self.windows_1234 == 3:  # 4
#                         os.system('play {}'.format(self.wav_arrive_hormone))
#                         rospy.loginfo("到达激素检验窗口")
#                     elif self.windows_1234 == 4:  # 3
#                         os.system('play {}'.format(self.wav_arrive_immune))
#                         rospy.loginfo("到达免疫检验窗口")
#                     elif self.windows_1234 == 5:  # 2
#                         os.system('play {}'.format(self.wav_arrive_humoral))
#                         rospy.loginfo("到达体液检验窗口")
#                     elif self.windows_1234 == 6:  # 1
#                         os.system('play {}'.format(self.wav_arrive_blood))
#                         rospy.loginfo("到达血常规检验窗口")
#
#                     # 播报样本数量
#                     if self.windows_count == 3:
#                         rospy.loginfo("样本数为3")
#                         os.system('play {}'.format(self.wav_count_3))
#                     elif self.windows_count == 2:
#                         rospy.loginfo("样本数为2")
#                         os.system('play {}'.format(self.wav_count_2))
#                     elif self.windows_count == 1:
#                         rospy.loginfo("样本数为1")
#                         os.system('play {}'.format(self.wav_count_1))
#
#     def move(self, goal):
#         """发送导航目标并等待结果"""
#         self.move_base.send_goal(goal)
#         finished_within_time = self.move_base.wait_for_result(rospy.Duration(60))
#         if not finished_within_time:
#             self.move_base.cancel_goal()
#             rospy.loginfo("Timed out achieving goal")
#         else:
#             state = self.move_base.get_state()
#             if state == GoalStatus.SUCCEEDED:
#                 rospy.loginfo("Goal succeeded!")
#                 return True
#         return False
#
#     def detect_result(self, msg):
#         """处理摄像头识别结果"""
#         if self.count == 10:
#             self.ram_result = msg.data
#             rospy.logwarn("self.ram_result: %s", self.ram_result)
#             self.windows_C = self.ram_result[0]
#             self.windows_A = self.ram_result[1]
#             self.windows_B = self.ram_result[2]
#             self.windows_count = self.ram_result[3]
#             self.windows_1234 = self.ram_result[4]
#
#     def shutdown(self):
#         """机器人关闭时的清理工作"""
#         rospy.loginfo("Stopping the robot...")
#         self.move_base.cancel_goal()
#         rospy.sleep(2)
#         self.cmd_vel_pub.publish(Twist())
#         rospy.sleep(1)
#
#
# if __name__ == '__main__':
#     try:
#         MoveBaseSquare()
#     except rospy.ROSInterruptException:
#         rospy.loginfo("Navigation test finished.")


# !/usr/bin/env python
# -*- coding: utf-8 -*-
import roslib
import rospy
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
from visualization_msgs.msg import Marker
from math import radians, pi
from std_msgs.msg import Int32
from std_msgs.msg import Int32MultiArray
from std_srvs.srv import Empty
import os
import random
import subprocess


class MoveBaseSquare():
    def __init__(self):
        rospy.init_node('nav_pharmacy', anonymous=False)
        rospy.on_shutdown(self.shutdown)

        # 角度和路径点初始化
        quaternions = list()
        euler_angles = (pi / 2, pi / 2, 5 * pi / 9, -5 * pi / 9, -pi / 2, -pi / 2, -pi / 2, 0, -pi, 0)
        for angle in euler_angles:
            q_angle = quaternion_from_euler(0, 0, angle, axes='sxyz')
            q = Quaternion(*q_angle)
            quaternions.append(q)

        # 将 waypoints 存储为类的属性
        self.waypoints = list()
        self.waypoints.append(Pose(Point(1.375, 2.215, 0), quaternions[0]))  # //C
        self.waypoints.append(Pose(Point(0.590, 2.645, 0), quaternions[1]))  # //A
        self.waypoints.append(Pose(Point(1.375, 3.100, 0), quaternions[2]))  # //B
        self.waypoints.append(Pose(Point(-0.900, 0.805, 0), quaternions[3]))  # //4
        self.waypoints.append(Pose(Point(-1.700, 1.232, 0), quaternions[4]))  # //3
        self.waypoints.append(Pose(Point(-0.877, 1.775, 0), quaternions[5]))  # //2
        self.waypoints.append(Pose(Point(-1.800, 2.281, 0), quaternions[6]))  # //1
        self.waypoints.append(Pose(Point(-0.035, -0.184, 0), quaternions[7]))  # 起点
        self.waypoints.append(Pose(Point(-0.640, 3.900, 0), quaternions[8]))  # 答题区(识别板2)
        self.waypoints.append(Pose(Point(0.840, 0.040, 0), quaternions[9]))  # 识别板1

        # 状态变量初始化
        self.count = 9
        self.windows_ABC = 0
        self.windows_A = 1
        self.windows_B = 1
        self.windows_C = 1
        self.windows_1234 = 3
        self.sample_count = 0  # 记录当前已取样本数
        self.failed_windows = []  # 记录导航失败的窗口

        # ROS发布者和订阅者
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.cam_sub = rospy.Subscriber('/cam_return', Int32MultiArray, self.detect_result, queue_size=10)
        self.ram_result = [1, 1, 1, 3, 4]
        rospy.sleep(1)

        # 导航相关初始化
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        self.move_base.wait_for_server(rospy.Duration(60))
        rospy.wait_for_service('/move_base/clear_costmaps')
        self.clear_costmaps_service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
        rospy.loginfo("Starting navigation...")

        # 语音文件路径定义
        self.audio_path = '/home/EPRobot/robot_ws/src/pharmacy_pkg/yuyinwenjian/'

        # 取样本窗口的语音文件
        self.wav_get_A = os.path.join(self.audio_path, '取到A窗口中的.wav')
        self.wav_get_B = os.path.join(self.audio_path, '取到B窗口中的.wav')
        self.wav_get_C = os.path.join(self.audio_path, '取到C窗口中的.wav')
        self.wav_get_AB = os.path.join(self.audio_path, '取到A、B窗口中的.wav')
        self.wav_get_AC = os.path.join(self.audio_path, '取到C、A窗口中的.wav')
        self.wav_get_BC = os.path.join(self.audio_path, '取到C、B窗口中的.wav')
        self.wav_get_ABC = os.path.join(self.audio_path, '取到C、A、B窗口中的.wav')

        # 样本类型语音文件
        self.wav_venous_blood = os.path.join(self.audio_path, '静脉血样本.wav')
        self.wav_saliva = os.path.join(self.audio_path, '唾液样本.wav')
        self.wav_tissue = os.path.join(self.audio_path, '组织样本.wav')
        self.wav_plasma = os.path.join(self.audio_path, '血浆样本.wav')

        # 样本数量语音文件
        self.wav_count_1 = os.path.join(self.audio_path, '样本数为1.wav')
        self.wav_count_2 = os.path.join(self.audio_path, '样本数为2.wav')
        self.wav_count_3 = os.path.join(self.audio_path, '样本数为3.wav')

        # 到达窗口语音文件
        self.wav_arrive_hormone = os.path.join(self.audio_path, '到达激素检验窗口.wav')
        self.wav_arrive_immune = os.path.join(self.audio_path, '到达免疫检测窗口.wav')
        self.wav_arrive_humoral = os.path.join(self.audio_path, '到达体液窗口.wav')
        self.wav_arrive_blood = os.path.join(self.audio_path, '到达血常规窗口.wav')

        # 窗口编号到语音文件的映射（修正版：0-3对应化验区1-4号窗口）
        self.window_id_to_sound = {
            0: self.wav_arrive_blood,  # 化验区1号窗口（血常规检验窗口）
            1: self.wav_arrive_humoral,  # 化验区2号窗口（体液检验窗口）
            2: self.wav_arrive_immune,  # 化验区3号窗口（免疫检测窗口）
            3: self.wav_arrive_hormone,  # 化验区4号窗口（激素检验窗口）
        }

        # 窗口ID到waypoint索引的映射
        self.window_to_waypoint = {
            'C': 0,
            'A': 1,
            'B': 2
        }

    def move(self, goal, window_name=None):
        """发送导航目标并等待结果，增加重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            rospy.loginfo("尝试导航到{} (尝试 {}/{})".format(
                window_name if window_name else "目标点", attempt + 1, max_retries))

            self.move_base.send_goal(goal)
            finished_within_time = self.move_base.wait_for_result(rospy.Duration(60))

            if not finished_within_time:
                self.move_base.cancel_goal()
                rospy.logwarn("导航超时，尝试 {} 失败".format(attempt + 1))
                self.clear_costmaps_service()  # 清除代价地图
                rospy.sleep(2)  # 等待2秒再重试
            else:
                state = self.move_base.get_state()
                if state == GoalStatus.SUCCEEDED:
                    rospy.loginfo("导航到{}成功!".format(window_name if window_name else "目标点"))
                    return True
                else:
                    rospy.logwarn("导航到{}失败，状态码: {} (尝试 {}/{})".format(
                        window_name if window_name else "目标点", state, attempt + 1, max_retries))
                    self.clear_costmaps_service()
                    rospy.sleep(2)

        rospy.logerr("导航到{}达到最大重试次数，任务失败".format(
            window_name if window_name else "目标点"))
        return False

    def detect_result(self, msg):
        """处理摄像头识别结果"""
        if self.count == 10:
            self.ram_result = msg.data
            rospy.logwarn("完整识别结果: {}".format(self.ram_result))
            self.windows_C = self.ram_result[0]
            self.windows_A = self.ram_result[1]
            self.windows_B = self.ram_result[2]
            self.windows_count = self.ram_result[3]
            self.windows_1234 = self.ram_result[4]
            rospy.loginfo("窗口状态: C={}, A={}, B={}".format(self.windows_C, self.windows_A, self.windows_B))
            rospy.loginfo("样本数量: {}".format(self.windows_count))
            rospy.loginfo("目标窗口: {}".format(self.windows_1234))
            self.sample_count = 0  # 重置样本计数器
            self.failed_windows = []  # 重置失败窗口列表

    def shutdown(self):
        """机器人关闭时的清理工作"""
        rospy.loginfo("Stopping the robot...")
        self.move_base.cancel_goal()
        rospy.sleep(2)
        self.cmd_vel_pub.publish(Twist())
        rospy.sleep(1)

    def play_sound(self, sound_file):
        """使用subprocess播放单个语音文件并处理错误（兼容低版本Python）"""
        if not os.path.exists(sound_file):
            rospy.logerr("语音文件不存在: {}".format(sound_file))
            return False

        try:
            # 使用subprocess.call替代subprocess.run，兼容Python 3.4及以下版本
            retcode = subprocess.call(['play', sound_file])
            if retcode == 0:
                rospy.loginfo("播放成功: {}".format(sound_file))
                return True
            else:
                rospy.logerr("播放失败: {}, 错误码: {}".format(sound_file, retcode))
                return False
        except OSError as e:
            rospy.logerr("播放失败: {}, 错误: {}".format(sound_file, e))
            return False

    def play_summary_voice(self):
        """播放总结语音：取到[窗口]中的[样本类型]"""
        # 确定窗口组合语音文件
        window_wav = None
        if self.windows_C == 1 and self.windows_A == 1 and self.windows_B == 1:
            window_wav = self.wav_get_ABC
        elif self.windows_C == 1 and self.windows_A == 1:
            window_wav = self.wav_get_AC
        elif self.windows_C == 1 and self.windows_B == 1:
            window_wav = self.wav_get_BC
        elif self.windows_A == 1 and self.windows_B == 1:
            window_wav = self.wav_get_AB
        elif self.windows_C == 1:
            window_wav = self.wav_get_C
        elif self.windows_A == 1:
            window_wav = self.wav_get_A
        elif self.windows_B == 1:
            window_wav = self.wav_get_B

        # 修正样本类型语音文件的映射逻辑（0-3对应化验区1-4号窗口）
        sample_wav = None
        if self.windows_1234 == 3:  # 对应化验区4号窗口（激素检验）→ 血浆样本
            sample_wav = self.wav_plasma
        elif self.windows_1234 == 2:  # 对应化验区3号窗口（免疫检测）→ 组织样本
            sample_wav = self.wav_tissue
        elif self.windows_1234 == 1:  # 对应化验区2号窗口（体液窗口）→ 唾液样本
            sample_wav = self.wav_saliva
        elif self.windows_1234 == 0:  # 对应化验区1号窗口（血常规窗口）→ 静脉血样本
            sample_wav = self.wav_venous_blood

        # 播放组合语音
        if window_wav and sample_wav:
            rospy.loginfo("准备播放总结语音: {} + {}".format(window_wav, sample_wav))
            self.play_sound(window_wav)
            self.play_sound(sample_wav)
            return True
        else:
            rospy.logerr("无法生成完整的总结语音")
            return False

    def navigate_to_window(self, window_name, waypoint_index):
        """导航到指定窗口并处理结果"""
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = self.waypoints[waypoint_index]

        rospy.loginfo("开始导航到{}窗口: {}".format(
            window_name, self.waypoints[waypoint_index]))

        move_result = self.move(goal, window_name)

        if move_result:
            rospy.loginfo("成功到达{}窗口，准备取样本".format(window_name))
            # 模拟取样本操作（实际项目中可能需要调用机械臂等操作）
            rospy.sleep(2)
            self.sample_count += 1
            rospy.loginfo("从{}窗口取样本成功，当前样本计数: {}".format(
                window_name, self.sample_count))
            return True
        else:
            rospy.logerr("导航到{}窗口失败，跳过此窗口".format(window_name))
            self.failed_windows.append(window_name)
            return False

    def main_loop(self):
        """主循环"""
        while not rospy.is_shutdown():
            # 状态机逻辑
            if self.count == 9:  # 从起点到识别区
                rospy.loginfo("从起点到识别区")
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[9]
                if self.move(goal, "识别区"):
                    rospy.loginfo("到达识别区，开始识别二维码")
                    self.count = 10
                    self.clear_costmaps_service()
                    rospy.sleep(5)  # 等待识别完成

            elif self.count == 10:  # 从起点到配药区
                rospy.loginfo('开始配药流程')

                # 重置样本计数器
                self.sample_count = 0
                total_samples = sum([self.windows_C, self.windows_A, self.windows_B])
                rospy.loginfo("需要取的样本总数: {}".format(total_samples))

                # 定义需要访问的窗口及其对应的waypoint索引
                windows_to_visit = []
                if self.windows_C == 1:
                    windows_to_visit.append(('C', self.window_to_waypoint['C']))
                if self.windows_A == 1:
                    windows_to_visit.append(('A', self.window_to_waypoint['A']))
                if self.windows_B == 1:
                    windows_to_visit.append(('B', self.window_to_waypoint['B']))

                # 按顺序导航到每个窗口
                for window_name, waypoint_index in windows_to_visit:
                    self.navigate_to_window(window_name, waypoint_index)

                # 所有窗口都尝试访问后，检查样本计数
                if self.sample_count == total_samples:
                    rospy.loginfo("成功取到所有样本，准备播放总结语音")
                    self.play_summary_voice()
                else:
                    rospy.logwarn("样本计数不匹配: 已取{}, 需要{}".format(
                        self.sample_count, total_samples))
                    rospy.logwarn("导航失败的窗口: {}".format(self.failed_windows))

                    # 即使有窗口失败，也继续流程（根据实际需求调整）
                    rospy.loginfo("继续执行后续流程，即使有窗口导航失败")
                    if self.sample_count > 0:  # 至少取到一个样本才播放总结语音
                        self.play_summary_voice()

                self.count = 11

            elif self.count == 11:  # 从配药区到答题区
                rospy.loginfo("从配药区到答题区")
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[8]
                if self.move(goal, "答题区"):
                    rospy.loginfo("到达答题区，准备进行答题")
                    self.count = 12
                    self.clear_costmaps_service()
                    rospy.sleep(1)

            elif self.count == 12:  # 从答题区到数字区
                rospy.loginfo("从答题区到数字区")
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[(6 - self.windows_1234)]  # 注意这里的索引映射
                if self.move(goal, "数字区窗口{}".format(self.windows_1234)):
                    rospy.loginfo("到达数字区窗口 {}".format(self.windows_1234))

                    # 播放到达窗口的语音
                    if self.windows_1234 in self.window_id_to_sound:
                        window_sound = self.window_id_to_sound[self.windows_1234]
                        rospy.loginfo("准备播放到达窗口语音: {}".format(window_sound))
                        self.play_sound(window_sound)
                    else:
                        rospy.logwarn("未定义窗口 {} 的语音文件".format(self.windows_1234))

                    # 播放样本数量语音
                    if self.windows_count == 3:
                        rospy.loginfo("准备播放样本数为3")
                        self.play_sound(self.wav_count_3)
                    elif self.windows_count == 2:
                        rospy.loginfo("准备播放样本数为2")
                        self.play_sound(self.wav_count_2)
                    elif self.windows_count == 1:
                        rospy.loginfo("准备播放样本数为1")
                        self.play_sound(self.wav_count_1)

                    self.count = 9
                    self.clear_costmaps_service()
                    rospy.sleep(1)


if __name__ == '__main__':
    try:
        MoveBaseSquare().main_loop()
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")
        