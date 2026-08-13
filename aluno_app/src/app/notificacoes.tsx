import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { aluno } from '@/services/api';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
  green: '#159B5E',
  red: '#E8433D',
};

const ICON_MAP: Record<string, { name: string; color: string }> = {
  grade: { name: 'grade', color: COLORS.purple },
  event: { name: 'event', color: COLORS.red },
  workspace_preemium: { name: 'workspace-premium', color: COLORS.purple },
  certificado: { name: 'workspace-premium', color: COLORS.purple },
  inscricao: { name: 'check-circle', color: COLORS.green },
  default: { name: 'bell-outline', color: COLORS.purple },
};

function getIconForNotification(item: any) {
  const iconKey = item.tipo || item.icon || item.type || 'default';
  return ICON_MAP[iconKey] || ICON_MAP.default;
}

function formatTimeAgo(dateStr: string) {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffH = Math.floor(diffMin / 60);
    const diffD = Math.floor(diffH / 24);
    if (diffMin < 1) return 'agora';
    if (diffMin < 60) return `há ${diffMin} min`;
    if (diffH < 24) return `há ${diffH} hora${diffH > 1 ? 's' : ''}`;
    if (diffD === 1) return 'ontem';
    return `há ${diffD} dias`;
  } catch {
    return dateStr;
  }
}

function isToday(dateStr: string) {
  if (!dateStr) return false;
  try {
    const date = new Date(dateStr);
    const now = new Date();
    return date.toDateString() === now.toDateString();
  } catch {
    return false;
  }
}

export default function NotificacoesScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [markingRead, setMarkingRead] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  async function loadNotifications() {
    try {
      setLoading(true);
      const data = await aluno.getNotificacoes();
      setNotifications(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar notificações:', err);
    } finally {
      setLoading(false);
    }
  }

  const onRefresh = useCallback(async () => {
    try {
      setRefreshing(true);
      const data = await aluno.getNotificacoes();
      setNotifications(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao atualizar notificações:', err);
    } finally {
      setRefreshing(false);
    }
  }, []);

  async function handleMarkAllRead() {
    try {
      setMarkingRead(true);
      await aluno.marcarNotificacoesLidas();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, lida: true, read: true, unread: false }))
      );
    } catch (err) {
      console.error('Erro ao marcar como lidas:', err);
    } finally {
      setMarkingRead(false);
    }
  }

  const todayNotifs = notifications.filter((n) => isToday(n.data || n.date || n.created_at));
  const earlierNotifs = notifications.filter((n) => !isToday(n.data || n.date || n.created_at));

  function renderNotification(item: any) {
    const iconInfo = getIconForNotification(item);
    const isUnread = !item.lida && !item.read && item.unread !== false;
    const iconBg = item.iconBg || iconInfo.color;

    return (
      <View
        key={item.id}
        style={[styles.notifCard, isUnread && styles.notifCardUnread]}
      >
        <View style={[styles.notifIconWrap, { backgroundColor: (iconBg || iconInfo.color) + '18' }]}>
          <MaterialCommunityIcons name={iconInfo.name as any} size={22} color={iconInfo.color} />
        </View>
        <View style={styles.notifInfo}>
          <Text style={[styles.notifText, isUnread && styles.notifTextUnread]}>
            {item.texto || item.text || item.mensagem || item.message || ''}
          </Text>
          <Text style={styles.notifTime}>
            {formatTimeAgo(item.data || item.date || item.created_at || item.time || '')}
          </Text>
        </View>
        {isUnread && <View style={styles.unreadDot} />}
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Notificações</Text>
        <TouchableOpacity onPress={handleMarkAllRead} disabled={markingRead}>
          <Text style={[styles.markRead, markingRead && { opacity: 0.5 }]}>
            {markingRead ? 'A marcar...' : 'Marcar lidas'}
          </Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color={COLORS.purple} />
        </View>
      ) : (
        <ScrollView
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.purple} />}
        >
          {/* HOJE Section */}
          {todayNotifs.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>HOJE</Text>
              {todayNotifs.map(renderNotification)}
            </>
          )}

          {/* ANTERIORES Section */}
          {earlierNotifs.length > 0 && (
            <>
              <Text style={[styles.sectionTitle, { marginTop: 24 }]}>ANTERIORES</Text>
              {earlierNotifs.map(renderNotification)}
            </>
          )}

          {notifications.length === 0 && (
            <View style={{ alignItems: 'center', marginTop: 60 }}>
              <MaterialCommunityIcons name="bell-off-outline" size={48} color={COLORS.gray} />
              <Text style={{ fontSize: 14, color: COLORS.gray, marginTop: 12, fontFamily: 'System' }}>
                Sem notificações
              </Text>
            </View>
          )}

          <View style={{ height: 40 }} />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  markRead: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.purple,
    fontFamily: 'System',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12,
    marginTop: 4,
  },
  notifCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 10,
    gap: 12,
  },
  notifCardUnread: {
    backgroundColor: COLORS.lightPurple,
    borderColor: COLORS.purple,
  },
  notifIconWrap: {
    width: 42,
    height: 42,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notifInfo: {
    flex: 1,
  },
  notifText: {
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
    lineHeight: 20,
  },
  notifTextUnread: {
    fontWeight: '700',
  },
  notifTime: {
    fontSize: 12,
    color: COLORS.gray,
    fontFamily: 'System',
    marginTop: 4,
  },
  unreadDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.purple,
  },
});
