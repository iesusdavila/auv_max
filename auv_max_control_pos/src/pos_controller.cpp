#include "rclcpp/rclcpp.hpp"
#include "auv_max_control_pos/control_profundidad.hpp"
#include "auv_max_control_pos/control_posxy.hpp"
#include "auv_max_control_pos/control_yaw.hpp" 
#include "auv_max_control_pos/control_pitch.hpp"
#include <nav_msgs/msg/odometry.hpp>
//#include <std_srvs/srv/set_float64.hpp>
#include <ncurses.h>

class TeleopControlNode : public rclcpp::Node {
public:
    TeleopControlNode() : Node("teleoperacion_node") {
        // Dejar el constructor vacío o solo para inicializaciones básicas
    }

    void keyboardThread() {
        // Similar a tu función init anterior, pero en un hilo separado
        initscr();
        cbreak();
        noecho();
        keypad(stdscr, TRUE);

        double targetProfundidad = -0.1;
        double targetPosXY = -5.0;
        double targetYaw = 0.0;
        double targetPitch = 0.0;

        control_profundidad_->setTargetProfundidad(targetProfundidad);
        control_posXY_->setTargetPosXY(targetPosXY);
        control_yaw_->setTargetYaw(targetYaw);
        control_pitch_->setTargetPitch(targetPitch);

        int ch;
        while (rclcpp::ok()) {
            clear();
            ch = getch();
            switch(ch) {
                case KEY_UP:
                    targetProfundidad += 0.1;
                    break;
                case KEY_DOWN:
                    targetProfundidad -= 0.1;
                    break;
                case KEY_LEFT:
                    targetPosXY += 0.1;
                    break;
                case KEY_RIGHT:
                    targetPosXY -= 0.1;
                    break;
                case 'a':
                    targetYaw += 0.1;
                    break;
                case 'd':
                    targetYaw -= 0.1;
                    break;
                case 'w':
                    targetPitch -= 0.1;
                    break;
                case 's':
                    targetPitch += 0.1;
                    break;
                case 'q':
                    endwin(); // Finalizar ncurses antes de salir
                    return; // Sale del bucle y del hilo
            }
            control_posXY_->setTargetPosXY(targetPosXY);
            control_profundidad_->setTargetProfundidad(targetProfundidad);
            control_yaw_->setTargetYaw(targetYaw);
            control_pitch_->setTargetPitch(targetPitch);
        }
        endwin();
    }

    void init() {
        control_profundidad_ = std::make_shared<auv_control_profundidad::ControlProfundidad>(shared_from_this());
        control_posXY_ = std::make_shared<auv_control_posxy::ControlPosXY>(shared_from_this());
        control_yaw_ = std::make_shared<auv_control_yaw::ControlYaw>(shared_from_this());
        control_pitch_ = std::make_shared<auv_control_pitch::ControlPitch>(shared_from_this());

        odometry_subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/model/auv_max/odometry", 10,
            [this](const nav_msgs::msg::Odometry::SharedPtr msg) {
                control_profundidad_->updateControl(msg);
                control_posXY_->updateControl(msg);
                control_yaw_->updateControl(msg);
                control_pitch_->updateControl(msg);
            });

        // Crear un hilo para la teleoperación
        std::thread keyboard_thread(&TeleopControlNode::keyboardThread, this);
        keyboard_thread.detach();
    }

private:
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odometry_subscription_;
    std::shared_ptr<auv_control_profundidad::ControlProfundidad> control_profundidad_;
    std::shared_ptr<auv_control_posxy::ControlPosXY> control_posXY_;
    std::shared_ptr<auv_control_yaw::ControlYaw> control_yaw_;
    std::shared_ptr<auv_control_pitch::ControlPitch> control_pitch_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TeleopControlNode>();
    node->init();  // Llama a la función init después de la creación del nodo
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
