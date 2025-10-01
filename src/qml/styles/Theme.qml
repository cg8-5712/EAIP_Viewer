// Theme.qml - 主题配置单例
pragma Singleton
import QtQuick 2.15

QtObject {
    id: theme

    // ==================== 颜色配置 ====================

    // 主色调
    readonly property color primaryColor: "#1976D2"        // 蓝色
    readonly property color primaryDark: "#1565C0"
    readonly property color primaryLight: "#42A5F5"

    // 辅助色
    readonly property color accentColor: "#FF5722"         // 橙红色
    readonly property color accentLight: "#FF7043"

    // 背景色
    readonly property color backgroundColor: "#FAFAFA"     // 浅灰
    readonly property color surfaceColor: "#FFFFFF"        // 白色
    readonly property color cardColor: "#FFFFFF"

    // 文字颜色
    readonly property color textColor: "#212121"           // 深灰黑
    readonly property color textSecondary: "#757575"       // 灰色
    readonly property color textDisabled: "#BDBDBD"        // 浅灰
    readonly property color textOnPrimary: "#FFFFFF"       // 白色（主色上的文字）

    // 边框和分割线
    readonly property color dividerColor: "#E0E0E0"
    readonly property color borderColor: "#BDBDBD"

    // 状态颜色
    readonly property color successColor: "#4CAF50"        // 绿色
    readonly property color warningColor: "#FFC107"        // 黄色
    readonly property color errorColor: "#F44336"          // 红色
    readonly property color infoColor: "#2196F3"           // 蓝色

    // 阴影
    readonly property color shadowColor: "#40000000"       // 半透明黑

    // ==================== 字体配置 ====================

    readonly property int fontSizeSmall: 12
    readonly property int fontSizeNormal: 14
    readonly property int fontSizeMedium: 16
    readonly property int fontSizeLarge: 18
    readonly property int fontSizeTitle: 24
    readonly property int fontSizeHeading: 32

    readonly property string fontFamily: "Microsoft YaHei UI"  // Windows
    // readonly property string fontFamily: "PingFang SC"      // macOS
    // readonly property string fontFamily: "Noto Sans CJK SC" // Linux

    // ==================== 间距配置 ====================

    readonly property int spacingTiny: 4
    readonly property int spacingSmall: 8
    readonly property int spacingNormal: 16
    readonly property int spacingMedium: 24
    readonly property int spacingLarge: 32
    readonly property int spacingHuge: 48

    // ==================== 圆角配置 ====================

    readonly property int radiusSmall: 4
    readonly property int radiusNormal: 8
    readonly property int radiusMedium: 12
    readonly property int radiusLarge: 16
    readonly property int radiusRound: 999  // 完全圆形

    // ==================== 尺寸配置 ====================

    // 按钮
    readonly property int buttonHeight: 40
    readonly property int buttonHeightSmall: 32
    readonly property int buttonHeightLarge: 48

    // 输入框
    readonly property int inputHeight: 40
    readonly property int inputHeightSmall: 32

    // 图标
    readonly property int iconSizeSmall: 16
    readonly property int iconSizeNormal: 24
    readonly property int iconSizeLarge: 32
    readonly property int iconSizeHuge: 48

    // 工具栏
    readonly property int toolbarHeight: 56
    readonly property int sidebarWidth: 240

    // ==================== 动画配置 ====================

    readonly property int animationDuration: 200
    readonly property int animationDurationSlow: 300
    readonly property int animationDurationFast: 150

    // ==================== 阴影配置 ====================

    readonly property int shadowRadius: 8
    readonly property int shadowOffsetY: 2
}
