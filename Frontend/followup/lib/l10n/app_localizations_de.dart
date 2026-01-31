// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for German (`de`).
class AppLocalizationsDe extends AppLocalizations {
  AppLocalizationsDe([String locale = 'de']) : super(locale);

  @override
  String get appName => 'FollowUP';

  @override
  String get login => 'Anmelden';

  @override
  String get loginToContinue => 'Anmelden um fortzufahren';

  @override
  String get loggingIn => 'Anmeldung...';

  @override
  String get username => 'Benutzername';

  @override
  String get enterUsername => 'Benutzernamen eingeben';

  @override
  String get password => 'Passwort';

  @override
  String get enterPassword => 'Passwort eingeben';

  @override
  String get backToHome => 'Zurück zur Startseite';

  @override
  String get testAccount => 'Testkonto:';

  @override
  String get testAccountAlice => 'Benutzer: alice / Passwort: alice123';

  @override
  String get testAccountDemo => 'Benutzer: demo / Passwort: demo123';

  @override
  String get home => 'Startseite';

  @override
  String get add => 'Hinzufügen';

  @override
  String get events => 'Veranstaltungen';

  @override
  String get logout => 'Abmelden';

  @override
  String get confirmLogout => 'Abmeldung bestätigen';

  @override
  String get confirmLogoutMessage => 'Möchten Sie sich wirklich abmelden?';

  @override
  String welcomeBack(String username) {
    return 'Willkommen zurück, $username';
  }

  @override
  String get addEventPrompt =>
      'Haben Sie heute neue Veranstaltungen hinzuzufügen?';

  @override
  String get textRecognition => 'Texterkennung';

  @override
  String get inputDescription => 'Beschreibung eingeben';

  @override
  String get imageRecognition => 'Bilderkennung';

  @override
  String get photoOrUpload => 'Foto oder Upload';

  @override
  String get followedEvents => 'Verfolgte Veranstaltungen';

  @override
  String get viewAll => 'Alle anzeigen';

  @override
  String get noFollowedEvents => 'Noch keine verfolgten Veranstaltungen';

  @override
  String get addEvent => 'Veranstaltung hinzufügen';

  @override
  String get addActivity => 'Veranstaltung hinzufügen';

  @override
  String get pasteDescription =>
      'Veranstaltungsbeschreibung einfügen, KI erkennt automatisch Zeit, Ort usw.';

  @override
  String get eventDescription => 'Veranstaltungsbeschreibung';

  @override
  String get eventDescriptionHint =>
      'z.B.: Nächsten Samstag um 19 Uhr gibt es ein Beethoven-Konzert in der Hamburger Philharmonie...';

  @override
  String get additionalNote => 'Zusätzliche Notiz (Optional)';

  @override
  String get uploadPoster =>
      'Veranstaltungsposter hochladen, KI erkennt automatisch Veranstaltungsinformationen';

  @override
  String get eventImage => 'Veranstaltungsbild';

  @override
  String get recognizeSchedule => 'Termin erkennen';

  @override
  String get aiRecognizing => 'KI erkennt Veranstaltungsinformationen...';

  @override
  String get schedulePreview => 'Terminvorschau';

  @override
  String get editActivity => 'Veranstaltung bearbeiten';

  @override
  String get confirmActivity => 'Veranstaltung bestätigen';

  @override
  String get eventTitle => 'Veranstaltungstitel';

  @override
  String get enterEventTitle => 'Veranstaltungstitel eingeben';

  @override
  String get startTime => 'Startzeit';

  @override
  String get endTime => 'Endzeit';

  @override
  String get selectDate => 'Datum auswählen';

  @override
  String get selectTime => 'Zeit auswählen';

  @override
  String get location => 'Ort';

  @override
  String get eventLocation => 'Veranstaltungsort';

  @override
  String get description => 'Beschreibung';

  @override
  String get eventDescriptionField => 'Veranstaltungsbeschreibung...';

  @override
  String get downloadIcs => 'ICS herunterladen';

  @override
  String get saveActivity => 'Veranstaltung speichern';

  @override
  String get saving => 'Wird gespeichert...';

  @override
  String get activitySaved => 'Veranstaltung gespeichert';

  @override
  String multipleEventsDetected(int count) {
    return '$count Veranstaltungen erkannt, nach links/rechts wischen zum Wechseln';
  }

  @override
  String get eventList => 'Veranstaltungsliste';

  @override
  String get allEvents => 'Alle Veranstaltungen';

  @override
  String get followed => 'Verfolgt';

  @override
  String get noEvents => 'Noch keine Veranstaltungen';

  @override
  String get noFollowedEventsYet => 'Noch keine verfolgten Veranstaltungen';

  @override
  String get deleteEvent => 'Veranstaltung löschen';

  @override
  String get deleteEventConfirm =>
      'Möchten Sie diese Veranstaltung wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.';

  @override
  String get delete => 'Löschen';

  @override
  String get cancel => 'Abbrechen';

  @override
  String get eventDeleted => 'Veranstaltung gelöscht';

  @override
  String get icsDownloaded => 'ICS-Datei heruntergeladen';

  @override
  String get downloadFailed => 'Download fehlgeschlagen';

  @override
  String get fileSaved => 'Datei gespeichert';

  @override
  String get pleaseEnterEventDescription =>
      'Bitte Veranstaltungsbeschreibung eingeben';

  @override
  String get pleaseSelectImage => 'Bitte ein Bild auswählen';

  @override
  String get pleaseEnterEventTitle => 'Bitte Veranstaltungstitel eingeben';

  @override
  String get pleaseSelectStartDate => 'Bitte Startdatum auswählen';

  @override
  String get landingHeroTitle => 'Verpassen Sie nie wieder eine Veranstaltung';

  @override
  String get landingHeroSubtitle =>
      'FollowUP ist Ihr intelligenter persönlicher Assistent zur Verfolgung von Veranstaltungen. Extrahiert automatisch Veranstaltungsinformationen aus Text oder Bildern, synchronisiert mit Ihrem Kalender und sendet rechtzeitige Erinnerungen.';

  @override
  String get getStarted => 'Jetzt starten';

  @override
  String get learnMore => 'Mehr erfahren';

  @override
  String get painPointsTitle => 'Haben Sie auch diese Probleme?';

  @override
  String get painPoint1Title => 'Verstreute Informationen';

  @override
  String get painPoint1Desc =>
      'Veranstaltungsinfos in E-Mails, Chats und sozialen Medien verstreut, schwer zu verfolgen';

  @override
  String get painPoint2Title => 'Mühsame manuelle Eingabe';

  @override
  String get painPoint2Desc =>
      'Manuelle Kalendereingabe ist zeitaufwändig und fehleranfällig';

  @override
  String get painPoint3Title => 'Leicht zu vergessen';

  @override
  String get painPoint3Desc =>
      'Wichtige Veranstaltungen verpasst wegen fehlender rechtzeitiger Erinnerungen';

  @override
  String get howItWorksTitle => 'So funktioniert es';

  @override
  String get step1Title => 'Informationen erfassen';

  @override
  String get step1Desc => 'Text einfügen oder Veranstaltungsposter hochladen';

  @override
  String get step2Title => 'KI-Erkennung';

  @override
  String get step2Desc =>
      'Intelligente Extraktion von Zeit, Ort und anderen wichtigen Infos';

  @override
  String get step3Title => 'Mit einem Klick speichern';

  @override
  String get step3Desc =>
      'Bestätigen und zum Kalender hinzufügen mit Erinnerungen';

  @override
  String get featuresTitle => 'Hauptfunktionen';

  @override
  String get feature1Title => 'Texterkennung';

  @override
  String get feature1Desc =>
      'Veranstaltungsbeschreibung einfügen und KI die Informationen extrahieren lassen';

  @override
  String get feature2Title => 'Bilderkennung';

  @override
  String get feature2Desc =>
      'Veranstaltungsposter hochladen zur automatischen Analyse';

  @override
  String get feature3Title => 'Kalendersynchronisierung';

  @override
  String get feature3Desc =>
      'Export im ICS-Format, Synchronisierung mit jeder Kalender-App';

  @override
  String get feature4Title => 'Veranstaltungen verfolgen';

  @override
  String get feature4Desc =>
      'Wichtige Veranstaltungen verfolgen für rechtzeitige Erinnerungen';

  @override
  String get demoTitle => 'Sehen Sie es in Aktion';

  @override
  String get demoDesc =>
      'Sehen Sie, wie FollowUP unordentliche Veranstaltungsinfos in organisierte Kalendereinträge verwandelt';

  @override
  String get tryNow => 'Jetzt ausprobieren';

  @override
  String get pricingTitle => 'Einfache, transparente Preise';

  @override
  String get pricingFree => 'Kostenlos';

  @override
  String get pricingFreePriceDesc => 'für den persönlichen Gebrauch';

  @override
  String get pricingFreeFeature1 => '10 Veranstaltungen pro Monat';

  @override
  String get pricingFreeFeature2 => 'Texterkennung';

  @override
  String get pricingFreeFeature3 => 'Basis-Kalenderexport';

  @override
  String get pricingPro => 'Pro';

  @override
  String get pricingProPrice => '€4,99';

  @override
  String get pricingProPriceDesc => '/Monat';

  @override
  String get pricingProFeature1 => 'Unbegrenzte Veranstaltungen';

  @override
  String get pricingProFeature2 => 'Bilderkennung';

  @override
  String get pricingProFeature3 => 'Prioritäts-KI-Verarbeitung';

  @override
  String get pricingProFeature4 => 'Erweiterte Erinnerungen';

  @override
  String get mostPopular => 'Am beliebtesten';

  @override
  String get startFreeTrial => 'Kostenlose Testversion starten';

  @override
  String get pricingTeam => 'Team';

  @override
  String get pricingTeamPrice => '€19,99';

  @override
  String get pricingTeamPriceDesc => '/Monat';

  @override
  String get pricingTeamFeature1 => 'Alles in Pro';

  @override
  String get pricingTeamFeature2 => 'Teamzusammenarbeit';

  @override
  String get pricingTeamFeature3 => 'Geteilte Kalender';

  @override
  String get pricingTeamFeature4 => 'Admin-Dashboard';

  @override
  String get contactSales => 'Vertrieb kontaktieren';

  @override
  String get faqTitle => 'Häufig gestellte Fragen';

  @override
  String get faq1Question =>
      'Welche Arten von Veranstaltungen kann FollowUP erkennen?';

  @override
  String get faq1Answer =>
      'FollowUP kann die meisten Veranstaltungsformate erkennen, einschließlich Konzerte, Meetings, Konferenzen, gesellschaftliche Zusammenkünfte und mehr. Es funktioniert sowohl mit formellen als auch informellen Veranstaltungsbeschreibungen.';

  @override
  String get faq2Question => 'Wie genau ist die KI-Erkennung?';

  @override
  String get faq2Answer =>
      'Unsere KI erreicht 95%+ Genauigkeit für Standardformate. Sie können die extrahierten Informationen vor dem Speichern jederzeit überprüfen und bearbeiten.';

  @override
  String get faq3Question =>
      'Kann ich mit Google Kalender oder Apple Kalender synchronisieren?';

  @override
  String get faq3Answer =>
      'Ja! Exportieren Sie Veranstaltungen als ICS-Dateien und importieren Sie sie in jede Kalender-App, einschließlich Google Kalender, Apple Kalender, Outlook und mehr.';

  @override
  String get faq4Question => 'Sind meine Daten sicher?';

  @override
  String get faq4Answer =>
      'Absolut. Wir verwenden branchenübliche Verschlüsselung und teilen Ihre Daten niemals mit Dritten. Ihre Veranstaltungen werden sicher gespeichert und sind nur für Sie zugänglich.';

  @override
  String get footerTagline => 'Ihr intelligenter Veranstaltungsassistent';

  @override
  String get footerProduct => 'Produkt';

  @override
  String get footerFeatures => 'Funktionen';

  @override
  String get footerPricing => 'Preise';

  @override
  String get footerCompany => 'Unternehmen';

  @override
  String get footerAbout => 'Über uns';

  @override
  String get footerContact => 'Kontakt';

  @override
  String get footerLegal => 'Rechtliches';

  @override
  String get footerPrivacy => 'Datenschutz';

  @override
  String get footerTerms => 'AGB';

  @override
  String get footerCopyright => '© 2025 FollowUP. Alle Rechte vorbehalten.';

  @override
  String get signIn => 'Anmelden';

  @override
  String get or => 'oder';

  @override
  String get privacyFirst => 'Datenschutz zuerst';

  @override
  String get quickSetup => '30 Sekunden Einrichtung';

  @override
  String get freeToStart => 'Kostenlos starten';

  @override
  String get painPointsSubtitle => 'Lebensereignisse kommen schnell';

  @override
  String get painPointsDesc =>
      'Wichtige Termine kommen als Screenshots, Poster, Nachrichten oder Sprachnotizen.\nManuell zum Kalender hinzufügen? Mühsam und leicht zu vergessen.';

  @override
  String get painPointNeedSimpler => 'Sie brauchen einen einfacheren Weg';

  @override
  String get painPointPhoto => 'Veranstaltungsposter-Screenshots';

  @override
  String get painPointMessage => 'Termine in Nachrichten';

  @override
  String get painPointFlyer => 'Flyer und Einladungen';

  @override
  String get painPointVoice => 'Sprachnotizen';

  @override
  String get captureStep => 'Erfassen';

  @override
  String get captureStepDesc => 'Foto, Text oder Sprache';

  @override
  String get understandStep => 'Verstehen';

  @override
  String get understandStepDesc => 'KI-Verarbeitung';

  @override
  String get confirmStep => 'Bestätigen';

  @override
  String get confirmStepDesc => 'Prüfen und bearbeiten';

  @override
  String get doneStep => 'Fertig';

  @override
  String get doneStepDesc => 'Zum Kalender hinzufügen';

  @override
  String get featurePrivacyTitle => 'Datenschutz zuerst';

  @override
  String get featurePrivacyDesc =>
      'Kein Konto erforderlich, Ihre Daten werden sicher gespeichert';

  @override
  String get featureSmartTitle => 'Intelligente Erkennung';

  @override
  String get featureSmartDesc =>
      'KI extrahiert automatisch Datum, Zeit, Ort und wichtige Infos';

  @override
  String get featureControlTitle => 'Volle Kontrolle';

  @override
  String get featureControlDesc =>
      'Ergebnisse vor der Bestätigung prüfen und bearbeiten';

  @override
  String get featureFocusSubtitle =>
      'Mentale Belastung reduzieren, auf das Leben konzentrieren';

  @override
  String get featureFocusDesc =>
      'FollowUP verwaltet leise Ihren Zeitplan, damit Sie sich auf das Wesentliche konzentrieren können';

  @override
  String get demoInputLabel => 'Eingabe';

  @override
  String get demoTextTab => 'Text';

  @override
  String get demoImageTab => 'Bild';

  @override
  String get demoVoiceTab => 'Sprache';

  @override
  String get demoInputPlaceholder =>
      'Text mit Veranstaltungsinformationen eingeben...';

  @override
  String get demoClickUpload => 'Klicken zum Hochladen';

  @override
  String get demoClickRecord => 'Klicken zum Aufnehmen';

  @override
  String get demoEventPreview => 'Veranstaltungsvorschau';

  @override
  String get demoTeamDinner => 'Team-Abendessen';

  @override
  String get demoRecognized => 'Erfolgreich erkannt';

  @override
  String get demoNextFriday => 'Nächsten Freitag 19:00';

  @override
  String get demoRestaurant => 'Olive Garden Restaurant · Hauptstraße';

  @override
  String get demoBirthdayCard => 'Sarahs Geburtstagskarte mitbringen';

  @override
  String get demoExtractedEvent => 'Extrahierte Veranstaltung erscheint hier';

  @override
  String get demoAddToCalendar => 'Zum Kalender hinzufügen';

  @override
  String get theProblem => 'Das Problem';

  @override
  String get stillHaveQuestions => 'Noch Fragen?';

  @override
  String get everythingYouNeed => 'Alles was Sie über FollowUP wissen müssen';

  @override
  String get footerCTATitle =>
      'Bereit, nie wieder eine Veranstaltung zu verpassen?';

  @override
  String get footerCTASubtitle =>
      'Starten Sie kostenlos mit FollowUP und lassen Sie KI Ihren Zeitplan verwalten';

  @override
  String get footerDescription =>
      'Verwandeln Sie Lebensmomente in Kalendereinträge\nNie wieder Sorgen über Vergessen';
}
