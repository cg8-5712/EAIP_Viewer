// main.qml - 应用主窗口
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15
import "styles"

ApplicationWindow {
    id: root

    width: 1280
    height: 720
    minimumWidth: 1024
    minimumHeight: 600
    visible: true
    title: "EAIP Viewer"

    // ==================== 属性 ====================

    property string currentPage: "welcome"

    // ==================== 背景 ====================

    background: Rectangle {
        color: Theme.backgroundColor
    }

    // ==================== 主布局 ====================

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 顶部工具栏
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.primaryColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingNormal

                // Logo 和标题
                RowLayout {
                    spacing: Theme.spacingSmall

                    Rectangle {
                        width: 40
                        height: 40
                        radius: Theme.radiusSmall
                        color: Theme.primaryLight

                        Text {
                            anchors.centerIn: parent
                            text: "EA"
                            font.pixelSize: Theme.fontSizeMedium
                            font.bold: true
                            color: Theme.textOnPrimary
                        }
                    }

                    Text {
                        text: "EAIP Viewer"
                        font.pixelSize: Theme.fontSizeLarge
                        font.bold: true
                        color: Theme.textOnPrimary
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                // 版本信息
                Text {
                    text: "v" + appVersion
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textOnPrimary
                    opacity: 0.8
                }
            }
        }

        // 内容区域
        StackView {
            id: stackView
            Layout.fillWidth: true
            Layout.fillHeight: true

            initialItem: welcomePage

            // 页面切换动画
            pushEnter: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: Theme.animationDuration
                }
            }

            pushExit: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: Theme.animationDuration
                }
            }
        }
    }

    // ==================== 欢迎页面 ====================

    Component {
        id: welcomePage

        Rectangle {
            color: Theme.backgroundColor

            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.spacingLarge

                // 欢迎图标
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 120
                    height: 120
                    radius: Theme.radiusLarge
                    color: Theme.primaryColor

                    Text {
                        anchors.centerIn: parent
                        text: "✈"
                        font.pixelSize: 64
                        color: Theme.textOnPrimary
                    }
                }

                // 欢迎文字
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "欢迎使用 EAIP Viewer"
                    font.pixelSize: Theme.fontSizeTitle
                    font.bold: true
                    color: Theme.textColor
                }

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "电子航空情报资料查看器"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textSecondary
                }

                // 开始按钮
                Button {
                    Layout.alignment: Qt.AlignHCenter
                    text: "开始使用"
                    font.pixelSize: Theme.fontSizeNormal
                    implicitWidth: 200
                    implicitHeight: Theme.buttonHeightLarge

                    background: Rectangle {
                        radius: Theme.radiusNormal
                        color: parent.pressed ? Theme.primaryDark :
                               parent.hovered ? Theme.primaryLight :
                               Theme.primaryColor

                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animationDurationFast
                            }
                        }
                    }

                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: Theme.textOnPrimary
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        console.log("开始使用按钮被点击")
                        // TODO: 跳转到登录页面
                        // stackView.push("pages/LoginPage.qml")
                    }
                }

                // 开发环境提示
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: isDevelopment ? "🛠 开发模式" : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.warningColor
                    visible: isDevelopment
                }
            }
        }
    }

    // ==================== 状态栏 ====================

    footer: Rectangle {
        height: 24
        color: Theme.surfaceColor

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: Theme.dividerColor
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacingNormal
            anchors.rightMargin: Theme.spacingNormal
            spacing: Theme.spacingNormal

            Text {
                text: "就绪"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
            }

            Item {
                Layout.fillWidth: true
            }

            Text {
                text: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary

                Timer {
                    interval: 1000
                    running: true
                    repeat: true
                    onTriggered: parent.text = Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
                }
            }
        }
    }
}
