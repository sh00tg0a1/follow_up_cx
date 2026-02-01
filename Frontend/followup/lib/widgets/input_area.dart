import 'package:flutter/material.dart';

// 文本输入区域组件
class TextInputArea extends StatelessWidget {
  final TextEditingController controller;
  final String hintText;
  final int maxLines;
  final int? maxLength;
  final String? labelText;
  final String? helperText;
  final ValueChanged<String>? onChanged;

  const TextInputArea({
    super.key,
    required this.controller,
    this.hintText = '请输入内容...',
    this.maxLines = 8,
    this.maxLength,
    this.labelText,
    this.helperText,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      maxLines: maxLines,
      maxLength: maxLength,
      onChanged: onChanged,
      decoration: InputDecoration(
        hintText: hintText,
        labelText: labelText,
        helperText: helperText,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Theme.of(context).colorScheme.surface,
        contentPadding: const EdgeInsets.all(16),
      ),
    );
  }
}

// 补充说明输入框
class AdditionalNoteInput extends StatelessWidget {
  final TextEditingController controller;

  const AdditionalNoteInput({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      maxLines: 2,
      decoration: InputDecoration(
        hintText: '添加补充说明（可选）...',
        prefixIcon: const Icon(Icons.note_add_outlined),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Theme.of(context).colorScheme.surface,
      ),
    );
  }
}
