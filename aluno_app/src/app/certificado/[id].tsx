import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
  green: '#159B5E',
};

export default function CertificadoDetailScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <MaterialCommunityIcons name="arrow-left" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Certificado</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Certificate Card */}
        <View style={styles.certCard}>
          <View style={styles.certBorder}>
            {/* Logo */}
            <View style={styles.logoWrap}>
              <MaterialCommunityIcons name="school" size={32} color={COLORS.purple} />
            </View>

            <Text style={styles.certLabel}>CERTIFICADO DE CONCLUSÃO</Text>

            <Text style={styles.certText}>Certificamos que</Text>
            <Text style={styles.certName}>Ana Tavares</Text>

            <Text style={styles.certText}>concluiu com aproveitamento</Text>
            <Text style={styles.courseName}>Inglês Profissional</Text>

            <View style={styles.divider} />

            {/* QR Code Placeholder */}
            <View style={styles.qrWrap}>
              <View style={styles.qrBox}>
                <MaterialCommunityIcons name="qrcode" size={60} color={COLORS.dark} />
              </View>
            </View>

            <Text style={styles.verifyCode}>EDU-2026-8F3A9</Text>
            <Text style={styles.verifyUrl}>verificar.edukangola.ao</Text>
          </View>
        </View>

        {/* Verification Banner */}
        <View style={styles.verifyBanner}>
          <View style={styles.verifyIconWrap}>
            <MaterialCommunityIcons name="shield-check" size={24} color={COLORS.green} />
          </View>
          <View style={styles.verifyInfo}>
            <Text style={styles.verifyTitle}>Autêntico e válido</Text>
            <Text style={styles.verifySubtitle}>Verificado publicamente via QR Code</Text>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity style={styles.downloadBtn} activeOpacity={0.8}>
            <MaterialCommunityIcons name="file-download-outline" size={22} color="#fff" />
            <Text style={styles.downloadBtnText}>Baixar PDF</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.shareBtn} activeOpacity={0.8}>
            <MaterialCommunityIcons name="share-variant" size={22} color={COLORS.purple} />
            <Text style={styles.shareBtnText}>Partilhar</Text>
          </TouchableOpacity>
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
  certCard: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 4,
    borderWidth: 2,
    borderColor: '#D4A843',
    marginBottom: 16,
  },
  certBorder: {
    borderWidth: 1,
    borderColor: '#E8D48B',
    borderRadius: 16,
    padding: 28,
    alignItems: 'center',
  },
  logoWrap: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: COLORS.lightPurple,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  certLabel: {
    fontSize: 13,
    fontWeight: '800',
    color: COLORS.dark,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 1.5,
    marginBottom: 20,
  },
  certText: {
    fontSize: 14,
    color: COLORS.gray,
    fontFamily: 'System',
    marginBottom: 6,
  },
  certName: {
    fontSize: 24,
    fontWeight: '800',
    color: COLORS.dark,
    fontFamily: 'System',
    marginBottom: 16,
  },
  courseName: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
    marginBottom: 20,
  },
  divider: {
    width: 60,
    height: 2,
    backgroundColor: COLORS.border,
    marginBottom: 20,
  },
  qrWrap: {
    marginBottom: 12,
  },
  qrBox: {
    width: 80,
    height: 80,
    backgroundColor: COLORS.bg,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  verifyCode: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
    letterSpacing: 1,
    marginBottom: 4,
  },
  verifyUrl: {
    fontSize: 12,
    color: COLORS.gray,
    fontFamily: 'System',
  },
  verifyBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E6F9EE',
    borderRadius: 14,
    padding: 16,
    gap: 12,
    marginBottom: 20,
  },
  verifyIconWrap: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  verifyInfo: {
    flex: 1,
  },
  verifyTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.green,
    fontFamily: 'System',
  },
  verifySubtitle: {
    fontSize: 12,
    color: COLORS.green,
    fontFamily: 'System',
    opacity: 0.8,
    marginTop: 2,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  downloadBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: COLORS.purple,
    borderRadius: 14,
    paddingVertical: 14,
  },
  downloadBtnText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#fff',
    fontFamily: 'System',
  },
  shareBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: COLORS.lightPurple,
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 20,
  },
  shareBtnText: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
  },
});
