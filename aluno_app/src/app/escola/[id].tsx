import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { centros } from '@/services/api';

const COLORS_BG = ['#EDE7FE', '#DDF3E8', '#FBF0D9'];
const COLORS_TEXT = ['#5B18E6', '#159B5E', '#B57A12'];

export default function SchoolProfileScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const [school, setSchool] = useState<any>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState('Sobre');

  useEffect(() => {
    loadSchool();
  }, [id]);

  async function loadSchool() {
    try {
      setLoading(true);
      const data = await centros.get(id as string);
      setSchool(data);
      setFollowing(data?.seguindo || data?.following || false);
      setCourses(data?.cursos || data?.courses || []);
    } catch (err) {
      console.error('Erro ao carregar centro:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFollow() {
    try {
      await centros.seguir(id as string);
      setFollowing(!following);
    } catch (err) {
      console.error('Erro ao seguir centro:', err);
    }
  }

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color="#5B18E6" />
        </View>
      </SafeAreaView>
    );
  }

  const abbr = school?.sigla || school?.abbr || (school?.nome || school?.name || '').substring(0, 2).toUpperCase();
  const colorIdx = (Number(id) || 0) % COLORS_BG.length;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerStripes} />
        <View style={styles.headerContent}>
          <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
            <MaterialCommunityIcons name="arrow-left" size={22} color="#ffffff" />
          </TouchableOpacity>
        </View>

        <View style={styles.profileSection}>
          <View style={[styles.avatar, { backgroundColor: COLORS_BG[colorIdx] }]}>
            <Text style={[styles.avatarText, { color: COLORS_TEXT[colorIdx] }]}>{abbr}</Text>
          </View>
          <View style={styles.nameRow}>
            <Text style={styles.schoolName}>{school?.nome || school?.name}</Text>
            {(school?.verificado || school?.verified) && (
              <MaterialCommunityIcons name="check-decagram" size={17} color="#ffffff" />
            )}
          </View>
          <Text style={styles.locationText}>{school?.localizacao || school?.location || ''}</Text>
        </View>
      </View>

      {/* Follow button */}
      <View style={styles.followContainer}>
        <TouchableOpacity
          style={[styles.followBtn, following && styles.followBtnActive]}
          onPress={handleFollow}
        >
          <MaterialCommunityIcons
            name={following ? 'check' : 'plus'}
            size={18}
            color={following ? '#ffffff' : '#5B18E6'}
          />
          <Text style={[styles.followText, following && styles.followTextActive]}>
            {following ? 'A seguir' : 'Seguir instituição'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Tabs */}
        <View style={styles.tabRow}>
          {['Sobre', 'Cursos', 'Avaliações'].map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tabItem, activeTab === tab && styles.tabItemActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                {tab}
              </Text>
              {activeTab === tab && <View style={styles.tabIndicator} />}
            </TouchableOpacity>
          ))}
        </View>

        {/* Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{school?.total_cursos || courses.length || 0}</Text>
            <Text style={styles.statLabel}>Cursos</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{school?.total_alunos || school?.alunos || '0'}</Text>
            <Text style={styles.statLabel}>Alunos</Text>
          </View>
          <View style={styles.statCard}>
            <View style={styles.ratingBadge}>
              <MaterialCommunityIcons name="star" size={14} color="#E8A63D" />
              <Text style={styles.statValue}>{school?.rating || '4,8'}</Text>
            </View>
            <Text style={styles.statLabel}>Avaliação</Text>
          </View>
        </View>

        {/* About */}
        {activeTab === 'Sobre' && (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Sobre</Text>
              <Text style={styles.description}>
                {school?.descricao || school?.description || 'Sem descrição disponível.'}
              </Text>
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Localização</Text>
              <View style={styles.mapPlaceholder}>
                <MaterialCommunityIcons name="map-outline" size={36} color="#8B8598" />
                <Text style={styles.mapText}>{school?.localizacao || school?.location || 'Angola'}</Text>
              </View>
            </View>
          </>
        )}

        {/* Courses */}
        {activeTab === 'Cursos' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Cursos ({courses.length})</Text>
            {courses.length > 0 ? (
              courses.map((course: any) => (
                <TouchableOpacity
                  key={course.id}
                  style={styles.courseCard}
                  onPress={() => router.push(`/curso/${course.id}`)}
                >
                  <View style={[styles.courseIcon, { backgroundColor: COLORS_BG[course.id % COLORS_BG.length] }]}>
                    <MaterialCommunityIcons name="school" size={22} color={COLORS_TEXT[course.id % COLORS_TEXT.length]} />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.courseName} numberOfLines={1}>{course.titulo || course.title}</Text>
                    <Text style={styles.courseMeta}>{course.duracao || ''} · {course.preco != null ? `${Number(course.preco).toLocaleString('pt-AO')} Kz` : 'Gratuito'}</Text>
                  </View>
                  <MaterialCommunityIcons name="chevron-right" size={20} color="#8B8598" />
                </TouchableOpacity>
              ))
            ) : (
              <Text style={{ color: '#8B8598', marginTop: 12 }}>Nenhum curso disponível</Text>
            )}
          </View>
        )}

        {/* Ratings */}
        {activeTab === 'Avaliações' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Avaliações</Text>
            <Text style={{ color: '#8B8598', marginTop: 12 }}>Sem avaliações ainda</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F6F5FA' },
  header: { backgroundColor: '#5B18E6', paddingTop: 10, paddingBottom: 24, paddingHorizontal: 20, overflow: 'hidden' },
  headerStripes: { ...StyleSheet.absoluteFillObject, opacity: 0.12, backgroundColor: 'transparent', borderTopWidth: 40, borderTopColor: 'rgba(255,255,255,0.08)', borderRightWidth: 40, borderRightColor: 'transparent' },
  headerContent: { flexDirection: 'row', alignItems: 'center' },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: 'rgba(255, 255, 255, 0.18)', alignItems: 'center', justifyContent: 'center' },
  profileSection: { alignItems: 'center', marginTop: 16 },
  avatar: { width: 72, height: 72, borderRadius: 20, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: 'rgba(255, 255, 255, 0.3)' },
  avatarText: { fontFamily: 'System', fontSize: 26, fontWeight: '800' },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 12 },
  schoolName: { fontFamily: 'System', fontSize: 18, fontWeight: '800', color: '#ffffff' },
  locationText: { fontFamily: 'System', fontSize: 12, fontWeight: '500', color: 'rgba(255,255,255,0.8)', marginTop: 4 },
  followContainer: { alignItems: 'center', paddingVertical: 14 },
  followBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 22, paddingVertical: 11, borderRadius: 12, borderWidth: 2, borderColor: '#5B18E6', backgroundColor: '#ffffff' },
  followBtnActive: { backgroundColor: '#5B18E6', borderColor: '#5B18E6' },
  followText: { fontFamily: 'System', fontSize: 14, fontWeight: '700', color: '#5B18E6' },
  followTextActive: { color: '#ffffff' },
  scrollContent: { paddingBottom: 30 },
  tabRow: { flexDirection: 'row', paddingHorizontal: 20, borderBottomWidth: 1, borderBottomColor: '#ECE8F3' },
  tabItem: { paddingVertical: 12, marginRight: 20, position: 'relative' },
  tabText: { fontFamily: 'System', fontSize: 14, fontWeight: '600', color: '#8B8598' },
  tabTextActive: { fontWeight: '800', color: '#5B18E6' },
  tabIndicator: { position: 'absolute', bottom: 0, left: 0, right: 0, height: 3, backgroundColor: '#5B18E6', borderRadius: 2 },
  statsRow: { flexDirection: 'row', paddingHorizontal: 20, marginTop: 18, gap: 12 },
  statCard: { flex: 1, backgroundColor: '#ffffff', borderRadius: 14, borderWidth: 1, borderColor: '#ECE8F3', paddingVertical: 14, alignItems: 'center', gap: 4 },
  statValue: { fontFamily: 'System', fontSize: 18, fontWeight: '800', color: '#1B1630' },
  statLabel: { fontFamily: 'System', fontSize: 11, fontWeight: '600', color: '#8B8598' },
  ratingBadge: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  section: { paddingHorizontal: 20, marginTop: 22 },
  sectionTitle: { fontFamily: 'System', fontSize: 16, fontWeight: '800', color: '#1B1630', marginBottom: 10 },
  description: { fontFamily: 'System', fontSize: 14, fontWeight: '500', color: '#4A4557', lineHeight: 22 },
  mapPlaceholder: { height: 140, backgroundColor: '#ECE8F3', borderRadius: 16, alignItems: 'center', justifyContent: 'center', gap: 8 },
  mapText: { fontFamily: 'System', fontSize: 13, fontWeight: '600', color: '#8B8598' },
  courseCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#ffffff', borderRadius: 14, borderWidth: 1, borderColor: '#ECE8F3', padding: 12, marginBottom: 10, gap: 12 },
  courseIcon: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  courseName: { fontFamily: 'System', fontSize: 14, fontWeight: '700', color: '#1B1630' },
  courseMeta: { fontFamily: 'System', fontSize: 11, fontWeight: '500', color: '#8B8598', marginTop: 2 },
});
