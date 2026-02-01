import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

// 认证状态管理
class AuthProvider extends ChangeNotifier {
  User? _user;
  String? _token;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  bool get isLoggedIn => _token != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // 初始化 - 检查本地存储的登录状态
  Future<void> init() async {
    _isLoading = true;
    notifyListeners();

    try {
      final token = await AuthService.getToken();
      if (token != null) {
        _token = token;
        final userId = await AuthService.getUserId();
        final username = await AuthService.getUsername();
        if (userId != null && username != null) {
          _user = User(id: userId, username: username);
        }
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // 登录
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await ApiService.login(username, password);
      _token = response.accessToken;
      _user = response.user;

      // 保存到本地存储
      await AuthService.saveToken(_token!);
      await AuthService.saveUser(_user!.id, _user!.username);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // 登出
  Future<void> logout() async {
    _token = null;
    _user = null;
    await AuthService.clearToken();
    notifyListeners();
  }

  // 清除错误
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
