// 日程/活动模型
class EventData {
  final int? id;
  final String title;
  final DateTime startTime;
  final DateTime? endTime;
  final String? location;
  final String? description;
  final String? sourceType;
  final bool isFollowed;

  EventData({
    this.id,
    required this.title,
    required this.startTime,
    this.endTime,
    this.location,
    this.description,
    this.sourceType,
    this.isFollowed = false,
  });

  factory EventData.fromJson(Map<String, dynamic> json) {
    return EventData(
      id: json['id'] as int?,
      title: json['title'] as String,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: json['end_time'] != null
          ? DateTime.parse(json['end_time'] as String)
          : null,
      location: json['location'] as String?,
      description: json['description'] as String?,
      sourceType: json['source_type'] as String?,
      isFollowed: json['is_followed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'start_time': startTime.toIso8601String(),
      if (endTime != null) 'end_time': endTime!.toIso8601String(),
      if (location != null) 'location': location,
      if (description != null) 'description': description,
      if (sourceType != null) 'source_type': sourceType,
      'is_followed': isFollowed,
    };
  }

  EventData copyWith({
    int? id,
    String? title,
    DateTime? startTime,
    DateTime? endTime,
    String? location,
    String? description,
    String? sourceType,
    bool? isFollowed,
  }) {
    return EventData(
      id: id ?? this.id,
      title: title ?? this.title,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      location: location ?? this.location,
      description: description ?? this.description,
      sourceType: sourceType ?? this.sourceType,
      isFollowed: isFollowed ?? this.isFollowed,
    );
  }
}

// 解析响应模型
class ParseResponse {
  final List<EventData> events;
  final String parseId;

  ParseResponse({
    required this.events,
    required this.parseId,
  });

  factory ParseResponse.fromJson(Map<String, dynamic> json) {
    return ParseResponse(
      events: (json['events'] as List)
          .map((e) => EventData.fromJson(e as Map<String, dynamic>))
          .toList(),
      parseId: json['parse_id'] as String,
    );
  }
}
