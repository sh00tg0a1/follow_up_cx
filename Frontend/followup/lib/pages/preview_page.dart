import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:path_provider/path_provider.dart';
import 'package:universal_html/html.dart' as html;
import '../l10n/app_localizations.dart';
import '../models/event.dart';
import '../providers/events_provider.dart';
import '../widgets/loading_overlay.dart';
import '../widgets/error_dialog.dart';
import '../utils/date_formatter.dart';
import '../theme/app_theme.dart';

// 日程预览/编辑页面
class PreviewPage extends StatefulWidget {
  const PreviewPage({super.key});

  @override
  State<PreviewPage> createState() => _PreviewPageState();
}

class _PreviewPageState extends State<PreviewPage> {
  late List<EventData> _events;
  int _currentIndex = 0;
  bool _isEditing = false;
  bool _isSaving = false;

  // 编辑表单控制器
  final _titleController = TextEditingController();
  final _locationController = TextEditingController();
  final _descriptionController = TextEditingController();
  DateTime? _startDate;
  TimeOfDay? _startTime;
  DateTime? _endDate;
  TimeOfDay? _endTime;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeFromArguments();
    });
  }

  void _initializeFromArguments() {
    final args =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
    if (args != null) {
      if (args['events'] != null) {
        setState(() {
          _events = List<EventData>.from(args['events']);
          _isEditing = args['isEditing'] ?? false;
          if (_events.isNotEmpty) {
            _loadEventToForm(_events[_currentIndex]);
          }
        });
      } else if (args['event'] != null) {
        setState(() {
          _events = [args['event'] as EventData];
          _isEditing = args['isEditing'] ?? true;
          _loadEventToForm(_events[0]);
        });
      }
    }
  }

  void _loadEventToForm(EventData event) {
    _titleController.text = event.title;
    _locationController.text = event.location ?? '';
    _descriptionController.text = event.description ?? '';
    _startDate = DateTime(
      event.startTime.year,
      event.startTime.month,
      event.startTime.day,
    );
    _startTime = TimeOfDay.fromDateTime(event.startTime);
    if (event.endTime != null) {
      _endDate = DateTime(
        event.endTime!.year,
        event.endTime!.month,
        event.endTime!.day,
      );
      _endTime = TimeOfDay.fromDateTime(event.endTime!);
    } else {
      _endDate = null;
      _endTime = null;
    }
  }

  EventData _getEventFromForm() {
    final currentEvent = _events[_currentIndex];
    final startDateTime = DateTime(
      _startDate!.year,
      _startDate!.month,
      _startDate!.day,
      _startTime?.hour ?? 0,
      _startTime?.minute ?? 0,
    );
    DateTime? endDateTime;
    if (_endDate != null && _endTime != null) {
      endDateTime = DateTime(
        _endDate!.year,
        _endDate!.month,
        _endDate!.day,
        _endTime!.hour,
        _endTime!.minute,
      );
    }

    return currentEvent.copyWith(
      title: _titleController.text.trim(),
      startTime: startDateTime,
      endTime: endDateTime,
      location: _locationController.text.trim().isNotEmpty
          ? _locationController.text.trim()
          : null,
      description: _descriptionController.text.trim().isNotEmpty
          ? _descriptionController.text.trim()
          : null,
    );
  }

  Future<void> _saveEvent() async {
    final l10n = AppLocalizations.of(context)!;
    if (_titleController.text.trim().isEmpty) {
      SnackBarHelper.showError(context, l10n.pleaseEnterEventTitle);
      return;
    }
    if (_startDate == null) {
      SnackBarHelper.showError(context, l10n.pleaseSelectStartDate);
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      final event = _getEventFromForm();
      final eventsProvider = context.read<EventsProvider>();
      final success = await eventsProvider.saveEvent(event);

      if (success && mounted) {
        SnackBarHelper.showSuccess(context, l10n.activitySaved);
        Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
      } else if (mounted && eventsProvider.error != null) {
        SnackBarHelper.showError(context, eventsProvider.error!);
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  Future<void> _downloadIcs() async {
    final event = _getEventFromForm();
    
    // 生成简单的 ICS 内容
    final icsContent = _generateIcsContent(event);
    final filename = '${event.title.replaceAll(RegExp(r'[^\w\s]'), '')}.ics';

    try {
      if (kIsWeb) {
        // Web 平台下载
        final blob = html.Blob([icsContent], 'text/calendar');
        final url = html.Url.createObjectUrlFromBlob(blob);
        final anchor = html.AnchorElement(href: url)
          ..setAttribute('download', filename)
          ..click();
        html.Url.revokeObjectUrl(url);
      } else {
        // Mobile platform save file
        final directory = await getApplicationDocumentsDirectory();
        final file = File('${directory.path}/$filename');
        await file.writeAsString(icsContent);
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          SnackBarHelper.showSuccess(context, '${l10n.fileSaved}: ${file.path}');
        }
      }
    } catch (e) {
      if (mounted) {
        final l10n = AppLocalizations.of(context)!;
        SnackBarHelper.showError(context, '${l10n.downloadFailed}: $e');
      }
    }
  }

  String _generateIcsContent(EventData event) {
    final now = DateTime.now();
    final uid = 'followup-${now.millisecondsSinceEpoch}@followup.app';
    
    String formatIcsDate(DateTime dt) {
      return '${dt.year}${dt.month.toString().padLeft(2, '0')}${dt.day.toString().padLeft(2, '0')}T'
          '${dt.hour.toString().padLeft(2, '0')}${dt.minute.toString().padLeft(2, '0')}00';
    }

    final buffer = StringBuffer();
    buffer.writeln('BEGIN:VCALENDAR');
    buffer.writeln('VERSION:2.0');
    buffer.writeln('PRODID:-//FollowUP//FollowUP App//EN');
    buffer.writeln('BEGIN:VEVENT');
    buffer.writeln('UID:$uid');
    buffer.writeln('DTSTAMP:${formatIcsDate(now)}');
    buffer.writeln('DTSTART:${formatIcsDate(event.startTime)}');
    if (event.endTime != null) {
      buffer.writeln('DTEND:${formatIcsDate(event.endTime!)}');
    }
    buffer.writeln('SUMMARY:${event.title}');
    if (event.location != null) {
      buffer.writeln('LOCATION:${event.location}');
    }
    if (event.description != null) {
      buffer.writeln('DESCRIPTION:${event.description}');
    }
    buffer.writeln('END:VEVENT');
    buffer.writeln('END:VCALENDAR');

    return buffer.toString();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _locationController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    // If data not initialized yet
    if (!mounted || _events.isEmpty) {
      return Scaffold(
        backgroundColor: AppColors.backgroundStart,
        appBar: AppBar(
          backgroundColor: AppColors.cardBg,
          title: Text(l10n.schedulePreview),
        ),
        body: const SimpleWarmBackground(
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return LoadingOverlay(
      isLoading: _isSaving,
      message: l10n.saving,
      child: Scaffold(
        backgroundColor: AppColors.backgroundStart,
        appBar: AppBar(
          backgroundColor: AppColors.cardBg,
          title: Text(_isEditing ? l10n.editActivity : l10n.confirmActivity),
          actions: [
            if (_events.length > 1)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Center(
                  child: Text(
                    '${_currentIndex + 1}/${_events.length}',
                    style: theme.textTheme.bodyMedium,
                  ),
                ),
              ),
          ],
        ),
        body: SimpleWarmBackground(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Multiple events detected hint
                if (_events.length > 1) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.info_outline,
                        color: AppColors.primary,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          l10n.multipleEventsDetected(_events.length),
                          style: theme.textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // 表单
              _buildForm(context),
            ],
          ),
        ),
        ),
        bottomNavigationBar: Container(
          color: AppColors.cardBg,
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _downloadIcs,
                      icon: const Icon(Icons.download),
                      label: Text(l10n.downloadIcs),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.primary,
                        side: const BorderSide(color: AppColors.primary),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: FilledButton.icon(
                      onPressed: _saveEvent,
                      icon: const Icon(Icons.save),
                      label: Text(l10n.saveActivity),
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildForm(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Title
        Text(
          '${l10n.eventTitle} *',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _titleController,
          decoration: InputDecoration(
            hintText: l10n.enterEventTitle,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            prefixIcon: const Icon(Icons.title),
          ),
        ),
        const SizedBox(height: 20),

        // Start time
        Text(
          '${l10n.startTime} *',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _DatePickerField(
                value: _startDate,
                hint: l10n.selectDate,
                onChanged: (date) {
                  setState(() {
                    _startDate = date;
                  });
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _TimePickerField(
                value: _startTime,
                hint: l10n.selectTime,
                onChanged: (time) {
                  setState(() {
                    _startTime = time;
                  });
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // End time
        Text(
          l10n.endTime,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _DatePickerField(
                value: _endDate,
                hint: l10n.selectDate,
                onChanged: (date) {
                  setState(() {
                    _endDate = date;
                  });
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _TimePickerField(
                value: _endTime,
                hint: l10n.selectTime,
                onChanged: (time) {
                  setState(() {
                    _endTime = time;
                  });
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // Location
        Text(
          l10n.location,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _locationController,
          decoration: InputDecoration(
            hintText: l10n.eventLocation,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            prefixIcon: const Icon(Icons.location_on_outlined),
          ),
        ),
        const SizedBox(height: 20),

        // Description
        Text(
          l10n.description,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _descriptionController,
          maxLines: 4,
          decoration: InputDecoration(
            hintText: l10n.eventDescriptionField,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            alignLabelWithHint: true,
          ),
        ),
        const SizedBox(height: 100),
      ],
    );
  }
}

// 日期选择器
class _DatePickerField extends StatelessWidget {
  final DateTime? value;
  final String hint;
  final ValueChanged<DateTime?> onChanged;

  const _DatePickerField({
    required this.value,
    required this.hint,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        final date = await showDatePicker(
          context: context,
          initialDate: value ?? DateTime.now(),
          firstDate: DateTime.now().subtract(const Duration(days: 365)),
          lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
        );
        if (date != null) {
          onChanged(date);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: InputDecorator(
        decoration: InputDecoration(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 12,
            vertical: 14,
          ),
          prefixIcon: const Icon(Icons.calendar_today, size: 20),
        ),
        child: Text(
          value != null ? DateFormatter.formatDateShort(value!) : hint,
          style: value == null
              ? TextStyle(color: Theme.of(context).hintColor)
              : null,
        ),
      ),
    );
  }
}

// 时间选择器
class _TimePickerField extends StatelessWidget {
  final TimeOfDay? value;
  final String hint;
  final ValueChanged<TimeOfDay?> onChanged;

  const _TimePickerField({
    required this.value,
    required this.hint,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () async {
        final time = await showTimePicker(
          context: context,
          initialTime: value ?? TimeOfDay.now(),
        );
        if (time != null) {
          onChanged(time);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: InputDecorator(
        decoration: InputDecoration(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 12,
            vertical: 14,
          ),
          prefixIcon: const Icon(Icons.access_time, size: 20),
        ),
        child: Text(
          value != null ? value!.format(context) : hint,
          style: value == null
              ? TextStyle(color: Theme.of(context).hintColor)
              : null,
        ),
      ),
    );
  }
}
