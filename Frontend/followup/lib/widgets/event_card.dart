import 'package:flutter/material.dart';
import '../models/event.dart';
import '../utils/date_formatter.dart';

// 活动卡片组件
class EventCard extends StatelessWidget {
  final EventData event;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;
  final VoidCallback? onToggleFollow;
  final VoidCallback? onDownloadIcs;
  final bool showActions;

  const EventCard({
    super.key,
    required this.event,
    this.onTap,
    this.onDelete,
    this.onToggleFollow,
    this.onDownloadIcs,
    this.showActions = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final countdown = DateFormatter.getCountdown(event.startTime);
    final isUpcoming = !event.startTime.isBefore(DateTime.now());

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题和关注按钮
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      event.title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (showActions && onToggleFollow != null)
                    IconButton(
                      icon: Icon(
                        event.isFollowed ? Icons.star : Icons.star_border,
                        color: event.isFollowed ? Colors.amber : Colors.grey,
                      ),
                      onPressed: onToggleFollow,
                      tooltip: event.isFollowed ? '取消关注' : '关注',
                      visualDensity: VisualDensity.compact,
                    ),
                ],
              ),
              const SizedBox(height: 8),
              
              // 日期时间
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    DateFormatter.formatDateTime(event.startTime),
                    style: theme.textTheme.bodyMedium,
                  ),
                  if (event.endTime != null) ...[
                    Text(
                      ' - ${DateFormatter.formatTime(event.endTime!)}',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 4),
              
              // 地点
              if (event.location != null && event.location!.isNotEmpty)
                Row(
                  children: [
                    Icon(
                      Icons.location_on_outlined,
                      size: 16,
                      color: theme.colorScheme.secondary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        event.location!,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              
              // 描述
              if (event.description != null && event.description!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  event.description!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              
              const SizedBox(height: 12),
              
              // 底部信息和操作
              Row(
                children: [
                  // 倒计时标签
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: isUpcoming
                          ? theme.colorScheme.primaryContainer
                          : theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      countdown,
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: isUpcoming
                            ? theme.colorScheme.onPrimaryContainer
                            : theme.colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  
                  // 来源类型标签
                  if (event.sourceType != null) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            event.sourceType == 'image'
                                ? Icons.image_outlined
                                : Icons.text_snippet_outlined,
                            size: 12,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            event.sourceType == 'image' ? '图片' : '文本',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  
                  const Spacer(),
                  
                  // 操作按钮
                  if (showActions) ...[
                    if (onDownloadIcs != null)
                      IconButton(
                        icon: const Icon(Icons.download_outlined, size: 20),
                        onPressed: onDownloadIcs,
                        tooltip: '下载 ICS',
                        visualDensity: VisualDensity.compact,
                      ),
                    if (onDelete != null)
                      IconButton(
                        icon: Icon(
                          Icons.delete_outline,
                          size: 20,
                          color: theme.colorScheme.error,
                        ),
                        onPressed: onDelete,
                        tooltip: '删除',
                        visualDensity: VisualDensity.compact,
                      ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
