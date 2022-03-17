#! /usr/bin/env python3

from pathlib import Path
import rospy
from tf import transformations
from MIR_X import mir_x
from MIR_Y import mir_y

from Wall_X import wall_x
from Wall_Y import wall_y
from Wall_Z import wall_z

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped

class parse_path_trafo():

    def __init__(self):
        rospy.init_node("parse_path_trafo_node")
        self.mir_x= mir_x()
        self.mir_y= mir_y()

        self.wall_x = wall_x()
        self.wall_y = wall_y()
        self.wall_z = wall_z()

        #print(mir_y)

        self.mir_pub = rospy.Publisher("mir_path", Path, queue_size= 1)
        self.ur_pub = rospy.Publisher("ur_path", Path, queue_size= 1)


        self.mir_path = Path()
        self.mir_path_point = PoseStamped()
        self.mir_path.header.frame_id = "map"
        self.mir_path.header.stamp = rospy.Time.now()
        self.ur_path = Path()
        self.ur_path_point = PoseStamped()
        self.ur_path.header.frame_id = "map"
        self.ur_path.header.stamp = rospy.Time.now()

        rospy.Subscriber("/wall_frame_base", PoseWithCovarianceStamped, self.wall_frame_cb)
        rospy.spin()



    def wall_frame_cb(self,PoseWithCovarianceStamped):
        self.x = PoseWithCovarianceStamped.pose.pose.position.x
        self.y = PoseWithCovarianceStamped.pose.pose.position.y
        self.z = PoseWithCovarianceStamped.pose.pose.position.z
        q1 = PoseWithCovarianceStamped.pose.pose.orientation.x
        q2 = PoseWithCovarianceStamped.pose.pose.orientation.y
        q3 = PoseWithCovarianceStamped.pose.pose.orientation.z
        q4 = PoseWithCovarianceStamped.pose.pose.orientation.w
        self.R = transformations.quaternion_matrix([q1,q2,q3,q4])

        self.run()


    def run(self):

        self.mir_path.poses = [PoseStamped() for i in range(len(self.mir_x))] 
        self.ur_path.poses = [PoseStamped() for i in range(len(self.wall_x))] 


        for i in range(0,len(self.mir_x)): #len(robot0_xhat)
            self.mir_path_point.pose.position.x = self.x + self.mir_x[i] * self.R[0][0] + self.mir_y[i] * self.R[0][1]
            self.mir_path_point.pose.position.y = self.y + self.mir_x[i] * self.R[1][0] + self.mir_y[i] * self.R[1][1]

            self.mir_path.poses[i].pose.position.x = self.mir_path_point.pose.position.x
            self.mir_path.poses[i].pose.position.y = self.mir_path_point.pose.position.y

        for i in range(0,len(self.wall_x)): #len(robot0_xhat)
            self.ur_path_point.pose.position.x = self.x + self.wall_x[i] * self.R[0][0] + self.wall_y[i] * self.R[0][1]
            self.ur_path_point.pose.position.y = self.y + self.wall_x[i] * self.R[1][0] + self.wall_y[i] * self.R[1][1]
            self.ur_path_point.pose.position.z = self.z + self.wall_z[i]

            self.ur_path.poses[i].pose.position.x = self.ur_path_point.pose.position.x
            self.ur_path.poses[i].pose.position.y = self.ur_path_point.pose.position.y
            self.ur_path.poses[i].pose.position.z = self.ur_path_point.pose.position.z

        self.mir_pub.publish(self.mir_path)
        rospy.sleep(0.01)
        self.ur_pub.publish(self.ur_path)



if __name__=="__main__":
    parse_path_trafo()
    