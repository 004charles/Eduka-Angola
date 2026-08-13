import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { perfil } from '@/services/api';
import { clearAll } from '@/services/storage';

const MENU_ITEMS = [
  { id: 1, icon: 'account-outline', label: 'Dados pessoais', route: '/dados-pessoais' },
  { id: 2, icon: 'credit-card-outline', label: 'Histórico de pagamentos', route: '/pagamentos' },
  { id: 3, icon: 'bell-outline', label: 'Notificações', route: '/notificacoes' },
  { id: 4, icon: 'translate', label: 'Idioma', right: 'Português (AO)' },
];

export default function PerfilScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      setLoading(true);
      const data = await perfil.get();
      setUser(data);
    } catch (err) {
      console.error('Erro ao carregar perfil:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await clearAll();
      router.replace('/login');
    } catch (err) {
      console.error('Erro ao terminar sessão:', err);
    }
  }

  const initials = user
    ? (user.first_name?.[0] || '') + (user.last_name?.[0] || user.username?.[0] || '')
    : 'AT';

  const displayName = user
    ? [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username || 'Estudante'
    : 'Ana Tavares';

  const email = user?.email || 'ana.tavares@email.com';
  const cursosCount = user?.total_cursos ?? user?.cursos_count ?? 5;
  const certificadosCount = user?.total_certificados ?? user?.certificados_count ?? 2;
  const horasEstudo = user?.horas_estudo ?? user?.study_hours ?? 48;

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />
        <View style={[styles.header, { alignItems: 'center', justifyContent: 'center' }]}>
          <ActivityIndicator size="large" color="#ffffff" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Purple gradient header */}
        <View style={styles.header}>
          <View style={styles.avatarWrap}>
            <Text style={styles.avatarText}>{initials}</Text>
          </View>
          <Text style={styles.userName}>{displayName}</Text>
          <Text style={styles.userEmail}>{email}</Text>
          <View style={styles.badgeRow}>
            <MaterialCommunityIcons name="school-outline" size={14} color="rgba(255,255,255,0.85)" />
            <Text style={styles.badgeLabel}>Estudante · Luanda</Text>
          </View>
        </View>

        {/* Stats row */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{cursosCount}</Text>
            <Text style={styles.statLabel}>Cursos</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{certificadosCount}</Text>
            <Text style={styles.statLabel}>Certificados</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{horasEstudo}h</Text>
            <Text style={styles.statLabel}>Estudo</Text>
          </View>
        </View>

        {/* Menu items */}
        <View style={styles.menuCard}>
          {MENU_ITEMS.map((item, idx) => (
            <TouchableOpacity
              key={item.id}
              style={[styles.menuItem, idx < MENU_ITEMS.length - 1 && styles.menuItemBorder]}
              activeOpacity={0.6}
              onPress={() => {
                if (item.route) router.push(item.route as any);
              }}
            >
              <View style={styles.menuIconWrap}>
                <MaterialCommunityIcons name={item.icon as any} size={22} color="#5B18E6" />
              </View>
              <Text style={styles.menuLabel}>{item.label}</Text>
              <View style={styles.menuRight}>
                {item.right && <Text style={styles.menuRightText}>{item.right}</Text>}
                <MaterialCommunityIcons name="chevron-right" size={20} color="#8B8598" />
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Logout */}
        <TouchableOpacity style={styles.logoutBtn} activeOpacity={0.7} onPress={handleLogout}>
          <MaterialCommunityIcons name="logout" size={20} color="#E8433D" />
          <Text style={styles.logoutText}>Terminar sessão</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F5FA',
  },
  scrollContent: {
    paddingBottom: 30,
  },
  header: {
    backgroundColor: '#5B18E6',
    paddingTop: 30,
    paddingBottom: 28,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  avatarWrap: {
    width: 72,
    height: 72,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderWidth: 3,
    borderColor: 'rgba(255,255,255,0.4)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 14,
  },
  avatarText: {
    fontFamily: 'System',
    fontSize: 26,
    fontWeight: '800',
    color: '#ffffff',
  },
  userName: {
    fontFamily: 'System',
    fontSize: 20,
    fontWeight: '800',
    color: '#ffffff',
  },
  userEmail: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.75)',
    marginTop: 3,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 10,
    backgroundColor: 'rgba(255,255,255,0.15)',
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 99,
  },
  badgeLabel: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#ffffff',
  },
  statsRow: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginTop: -16,
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    paddingVertical: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontFamily: 'System',
    fontSize: 20,
    fontWeight: '800',
    color: '#1B1630',
  },
  statLabel: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '600',
    color: '#8B8598',
    marginTop: 3,
  },
  statDivider: {
    width: 1,
    height: '70%',
    alignSelf: 'center',
    backgroundColor: '#ECE8F3',
  },
  menuCard: {
    marginHorizontal: 20,
    marginTop: 20,
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    overflow: 'hidden',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 15,
    gap: 12,
  },
  menuItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: '#ECE8F3',
  },
  menuIconWrap: {
    width: 38,
    height: 38,
    borderRadius: 11,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  menuLabel: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '700',
    color: '#1B1630',
  },
  menuRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  menuRightText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
  },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 20,
    marginTop: 24,
    backgroundColor: '#FDECEC',
    borderRadius: 16,
    paddingVertical: 15,
    gap: 8,
  },
  logoutText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#E8433D',
  },
});
