import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../providers/events_provider.dart';
import '../widgets/input_area.dart';
import '../widgets/image_picker_widget.dart';
import '../widgets/loading_overlay.dart';
import '../widgets/error_dialog.dart';
import '../theme/app_theme.dart';

// 输入页面
class InputPage extends StatefulWidget {
  const InputPage({super.key});

  @override
  State<InputPage> createState() => _InputPageState();
}

class _InputPageState extends State<InputPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _textController = TextEditingController();
  final _noteController = TextEditingController();
  String? _imageBase64;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    // 检查是否有传入的参数
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final args =
          ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
      if (args != null && args['tab'] != null) {
        _tabController.animateTo(args['tab'] as int);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _textController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _parseEvent() async {
    final l10n = AppLocalizations.of(context)!;
    final isTextMode = _tabController.index == 0;

    // Validate input
    if (isTextMode && _textController.text.trim().isEmpty) {
      SnackBarHelper.showError(context, l10n.pleaseEnterEventDescription);
      return;
    }
    if (!isTextMode && _imageBase64 == null) {
      SnackBarHelper.showError(context, l10n.pleaseSelectImage);
      return;
    }

    final eventsProvider = context.read<EventsProvider>();
    final success = await eventsProvider.parseEvent(
      inputType: isTextMode ? 'text' : 'image',
      textContent: isTextMode ? _textController.text.trim() : null,
      imageBase64: isTextMode ? null : _imageBase64,
      additionalNote: _noteController.text.trim().isNotEmpty
          ? _noteController.text.trim()
          : null,
    );

    if (success && mounted) {
      // 跳转到预览页面
      Navigator.pushNamed(
        context,
        '/preview',
        arguments: {
          'events': eventsProvider.parsedEvents,
          'isEditing': false,
        },
      );
    } else if (mounted && eventsProvider.error != null) {
      SnackBarHelper.showError(context, eventsProvider.error!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Consumer<EventsProvider>(
      builder: (context, eventsProvider, child) {
        return LoadingOverlay(
          isLoading: eventsProvider.isParsing,
          message: l10n.aiRecognizing,
          child: Scaffold(
            backgroundColor: AppColors.backgroundStart,
            appBar: AppBar(
              backgroundColor: AppColors.cardBg,
              title: Text(l10n.addActivity),
              bottom: TabBar(
                controller: _tabController,
                labelColor: AppColors.primary,
                indicatorColor: AppColors.primary,
                tabs: [
                  Tab(
                    icon: const Icon(Icons.text_snippet),
                    text: l10n.textRecognition,
                  ),
                  Tab(
                    icon: const Icon(Icons.image),
                    text: l10n.imageRecognition,
                  ),
                ],
              ),
            ),
            body: SimpleWarmBackground(
              child: TabBarView(
              controller: _tabController,
              children: [
                // 文字输入 Tab
                _TextInputTab(
                  textController: _textController,
                  noteController: _noteController,
                ),
                // 图片上传 Tab
                _ImageInputTab(
                  noteController: _noteController,
                  onImageSelected: (base64) {
                    setState(() {
                      _imageBase64 = base64;
                    });
                  },
                ),
              ],
            ),
            ),
            bottomNavigationBar: Container(
              color: AppColors.cardBg,
              child: SafeArea(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: FilledButton.icon(
                    onPressed: eventsProvider.isParsing ? null : _parseEvent,
                    icon: const Icon(Icons.auto_awesome),
                    label: Text(l10n.recognizeSchedule),
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _TextInputTab extends StatelessWidget {
  final TextEditingController textController;
  final TextEditingController noteController;

  const _TextInputTab({
    required this.textController,
    required this.noteController,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    l10n.pasteDescription,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Text input area
          Text(
            l10n.eventDescription,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          TextInputArea(
            controller: textController,
            hintText: l10n.eventDescriptionHint,
            maxLines: 10,
          ),
          const SizedBox(height: 24),

          // Additional note
          Text(
            l10n.additionalNote,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          AdditionalNoteInput(controller: noteController),
          const SizedBox(height: 100),
        ],
      ),
    );
  }
}

class _ImageInputTab extends StatelessWidget {
  final TextEditingController noteController;
  final ValueChanged<String?> onImageSelected;

  const _ImageInputTab({
    required this.noteController,
    required this.onImageSelected,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    l10n.uploadPoster,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Image picker area
          Text(
            l10n.eventImage,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ImagePickerWidget(onImageSelected: onImageSelected),
          const SizedBox(height: 24),

          // Additional note
          Text(
            l10n.additionalNote,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          AdditionalNoteInput(controller: noteController),
          const SizedBox(height: 100),
        ],
      ),
    );
  }
}
