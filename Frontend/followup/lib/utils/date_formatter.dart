import 'package:intl/intl.dart';

class DateFormatter {
  // 格式化日期：2026年2月15日
  static String formatDate(DateTime date) {
    return DateFormat('yyyy年M月d日').format(date);
  }

  // 格式化时间：19:30
  static String formatTime(DateTime time) {
    return DateFormat('HH:mm').format(time);
  }

  // 格式化日期时间：2026年2月15日 19:30
  static String formatDateTime(DateTime dateTime) {
    return DateFormat('yyyy年M月d日 HH:mm').format(dateTime);
  }

  // 格式化日期（短格式）：2/15
  static String formatDateShort(DateTime date) {
    return DateFormat('M/d').format(date);
  }

  // 格式化星期：周六
  static String formatWeekday(DateTime date) {
    const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return weekdays[date.weekday - 1];
  }

  // 计算倒计时
  static String getCountdown(DateTime eventDate) {
    final now = DateTime.now();
    final difference = eventDate.difference(now);

    if (difference.isNegative) {
      return '已结束';
    }

    if (difference.inDays > 0) {
      return '${difference.inDays}天后';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时后';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟后';
    } else {
      return '即将开始';
    }
  }

  // 格式化时间范围
  static String formatTimeRange(DateTime start, DateTime? end) {
    final startStr = formatTime(start);
    if (end == null) {
      return startStr;
    }
    return '$startStr - ${formatTime(end)}';
  }
}
