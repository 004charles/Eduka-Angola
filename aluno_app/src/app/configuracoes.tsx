import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, Switch } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
};

export default function ConfiguracoesScreen() {
  const router = useRouter();
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [wifiOnly, setWifiOnly] = useState(true);
  const [biometric, setBiometric] = useState(true);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Configurações</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* PREFERÊNCIAS */}
        <Text style={styles.sectionTitle}>PREFERÊNCIAS</Text>
        <View style={styles.sectionCard}>
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#EDE9FE' }]}>
                <MaterialCommunityIcons name="weather-night" size={20} color={COLORS.purple} />
              </View>
              <Text style={styles.settingLabel}>Modo escuro</Text>
            </View>
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
              trackColor={{ false: COLORS.border, true: COLORS.lightPurple }}
              thumbColor={darkMode ? COLORS.purple : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingDivider} />

          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#FEF3C7' }]}>
                <MaterialCommunityIcons name="bell-outline" size={20} color="#F59E0B" />
              </View>
              <Text style={styles.settingLabel}>Notificações push</Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: COLORS.border, true: COLORS.lightPurple }}
              thumbColor={notifications ? COLORS.purple : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingDivider} />

          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#DCFCE7' }]}>
                <MaterialCommunityIcons name="translate" size={20} color="#22C55E" />
              </View>
              <Text style={styles.settingLabel}>Idioma</Text>
            </View>
            <View style={styles.settingRight}>
              <Text style={styles.settingValue}>Português (AO)</Text>
              <Ionicons name="chevron-forward" size={18} color={COLORS.gray} />
            </View>
          </View>
        </View>

        {/* DOWNLOADS & ARMAZENAMENTO */}
        <Text style={styles.sectionTitle}>DOWNLOADS & ARMAZENAMENTO</Text>
        <View style={styles.sectionCard}>
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#EDE9FE' }]}>
                <MaterialCommunityIcons name="wifi" size={20} color={COLORS.purple} />
              </View>
              <Text style={styles.settingLabel}>Descarregar só em Wi-Fi</Text>
            </View>
            <Switch
              value={wifiOnly}
              onValueChange={setWifiOnly}
              trackColor={{ false: COLORS.border, true: COLORS.lightPurple }}
              thumbColor={wifiOnly ? COLORS.purple : '#f4f3f4'}
            />
          </View>

          <View style={styles.settingDivider} />

          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#FEE2E2' }]}>
                <MaterialCommunityIcons name="delete-outline" size={20} color="#EF4444" />
              </View>
              <Text style={styles.settingLabel}>Limpar downloads</Text>
            </View>
            <View style={styles.settingRight}>
              <Text style={styles.settingValueRed}>1,2 GB</Text>
            </View>
          </View>
        </View>

        {/* SEGURANÇA */}
        <Text style={styles.sectionTitle}>SEGURANÇA</Text>
        <View style={styles.sectionCard}>
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <View style={[styles.settingIcon, { backgroundColor: '#DCFCE7' }]}>
                <MaterialCommunityIcons name="fingerprint" size={20} color="#22C55E" />
              </View>
              <Text style={styles.settingLabel}>Autenticação biométrica</Text>
            </View>
            <Switch
              value={biometric}
              onValueChange={setBiometric}
              trackColor={{ false: COLORS.border, true: COLORS.lightPurple }}
              thumbColor={biometric ? COLORS.purple : '#f4f3f4'}
            />
          </View>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
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
    backgroundColor: COLORS.bg,
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
    marginBottom: 10,
    marginTop: 8,
  },
  sectionCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: 20,
    overflow: 'hidden',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  settingIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  settingRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  settingValue: {
    fontSize: 14,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  settingValueRed: {
    fontSize: 14,
    fontWeight: '600',
    color: '#EF4444',
    fontFamily: 'System',
  },
  settingDivider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginLeft: 64,
  },
});
