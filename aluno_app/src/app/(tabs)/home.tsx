import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Image, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { cursos, perfil, categorias, videoCursos, centros, parcerias } from '@/services/api';

export default function HomeScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [profile, setProfile] = useState<{ nome?: string; avatar?: string } | null>(null);
  const [recommended, setRecommended] = useState<any[]>([]);
  const [categoryList, setCategoryList] = useState<any[]>([]);
  const [videoList, setVideoList] = useState<any[]>([]);
  const [partnerList, setPartnerList] = useState<any[]>([]);
  const [popularCourses, setPopularCourses] = useState<any[]>([]);
  const [schools, setSchools] = useState<any[]>([]);

  const fetchData = useCallback(async () => {
    try {
      const [profileData, coursesData, catsData, videosData, schoolsData, partnersData] = await Promise.allSettled([
        perfil.get(),
        cursos.list(),
        categorias.list(),
        videoCursos.list(),
        centros.list(),
        parcerias.list(),
      ]);
      if (profileData.status === 'fulfilled') setProfile(profileData.value);
      
      const list = coursesData.status === 'fulfilled'
        ? (Array.isArray(coursesData.value) ? coursesData.value : (coursesData.value as any).results ?? [])
        : [];
      setRecommended(list.slice(0, 6));
      setPopularCourses(list.slice(0, 10));
      
      const cats = catsData.status === 'fulfilled'
        ? (Array.isArray(catsData.value) ? catsData.value : (catsData.value as any).results ?? [])
        : [];
      setCategoryList(cats);
      
      const vids = videosData.status === 'fulfilled'
        ? (Array.isArray(videosData.value) ? videosData.value : (videosData.value as any).results ?? [])
        : [];
      setVideoList(vids);
      
      const sch = schoolsData.status === 'fulfilled'
        ? (Array.isArray(schoolsData.value) ? schoolsData.value : (schoolsData.value as any).results ?? [])
        : [];
      setSchools(sch);

      const pars = partnersData.status === 'fulfilled'
        ? (Array.isArray(partnersData.value) ? partnersData.value : (partnersData.value as any).results ?? [])
        : [];
      setPartnerList(pars);
    } catch (err) {
      console.error('Failed to load home data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchData();
  }, [fetchData]);

  const firstName = profile?.nome?.split(' ')[0] ?? 'Estudante';
  const initials = profile?.nome
    ? profile.nome.split(' ').map((n: string) => n[0]).slice(0, 2).join('').toUpperCase()
    : 'AT';

  const badgeColors = [
    { bg: '#EDE7FE', text: '#5B18E6' },
    { bg: '#DDF3E8', text: '#159B5E' },
    { bg: '#FBF0D9', text: '#B57A12' },
    { bg: '#FDE7E7', text: '#E8433D' },
    { bg: '#E7F0FD', text: '#3B7DD8' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#5B18E6" />}
      >
        {/* User Profile Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>{initials}</Text>
          </View>
          <View style={styles.welcomeContainer}>
            <Text style={styles.welcomeLabel}>Bom dia,</Text>
            <Text style={styles.studentName}>{firstName}</Text>
          </View>
          <TouchableOpacity style={styles.notificationButton}>
            <MaterialCommunityIcons name="bell-outline" size={22} color="#4A4557" />
            <View style={styles.notificationDot} />
          </TouchableOpacity>
        </View>

        {/* Search Bar */}
        <TouchableOpacity style={styles.searchBar} onPress={() => router.push('/(tabs)/cursos')}>
          <MaterialCommunityIcons name="magnify" size={20} color="#9A93AD" />
          <Text style={styles.searchPlaceholder}>Procurar cursos, áreas…</Text>
        </TouchableOpacity>

        {/* Categories Horizontal Scroll */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesContainer}
        >
          <TouchableOpacity style={[styles.categoryPill, styles.categoryPillActive]}>
            <Text style={[styles.categoryText, styles.categoryTextActive]}>Todos</Text>
          </TouchableOpacity>
          {categoryList.slice(0, 8).map((cat) => (
            <TouchableOpacity
              key={cat.id}
              style={styles.categoryPill}
              onPress={() => router.push('/(tabs)/cursos')}
            >
              <Text style={styles.categoryText}>{cat.nome}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Continue Learning card */}
        <View style={styles.continueCard}>
          <Text style={styles.continueTag}>Continuar a aprender</Text>
          <Text style={styles.courseTitle}>Introdução à Programação Web</Text>
          <Text style={styles.lessonSub}>Módulo 2 · Aula 4 de 12</Text>

          {/* Progress bar */}
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: '45%' }]} />
          </View>

          {/* Play Overlay button */}
          <TouchableOpacity style={styles.playButton}>
            <MaterialCommunityIcons name="play" size={24} color="#ffffff" />
          </TouchableOpacity>
        </View>

        {/* Recommended Title */}
        <View style={styles.sectionTitleRow}>
          <Text style={styles.sectionTitle}>Recomendados</Text>
          <TouchableOpacity onPress={() => router.push('/(tabs)/cursos')}>
            <Text style={styles.seeAllText}>Ver todos</Text>
          </TouchableOpacity>
        </View>

        {/* Recommended Cards horizontal scroll */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.recommendedContainer}
        >
          {loading ? (
            <Text style={{ color: '#8B8598', paddingHorizontal: 20 }}>A carregar…</Text>
          ) : recommended.length > 0 ? (
            recommended.map((course, index) => {
              const color = badgeColors[index % badgeColors.length];
              return (
                <TouchableOpacity
                  key={course.id}
                  style={styles.courseCard}
                  activeOpacity={0.7}
                  onPress={() => router.push(`/curso/${course.id}`)}
                >
                  <View style={[styles.imagePlaceholder, { backgroundColor: color.bg }]}>
                    <MaterialCommunityIcons name="school" size={24} color={color.text} />
                  </View>
                  <View style={styles.cardInfo}>
                    <View style={[styles.categoryBadgePurple, { backgroundColor: color.bg }]}>
                      <Text style={[styles.badgeTextPurple, { color: color.text }]}>{course.categoria_nome ?? 'Curso'}</Text>
                    </View>
                    <Text style={styles.cardCourseTitle} numberOfLines={2}>{course.titulo ?? course.title}</Text>
                    <Text style={styles.cardCenterName}>{course.centro_nome ?? course.institution ?? ''}</Text>
                  </View>
                </TouchableOpacity>
              );
            })
          ) : (
            <Text style={{ color: '#8B8598', paddingHorizontal: 20 }}>Nenhum curso encontrado</Text>
          )}
        </ScrollView>

        {/* Video Cursos Section */}
        {videoList.length > 0 && (
          <>
            <View style={styles.sectionTitleRow}>
              <Text style={styles.sectionTitle}>Cursos em Vídeo</Text>
              <TouchableOpacity onPress={() => router.push('/(tabs)/aprendizagem')}>
                <Text style={styles.seeAllText}>Ver todos</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.recommendedContainer}
            >
              {videoList.slice(0, 5).map((vc, index) => {
                const color = badgeColors[(index + 2) % badgeColors.length];
                return (
                  <TouchableOpacity
                    key={vc.id}
                    style={styles.courseCard}
                    activeOpacity={0.7}
                    onPress={() => router.push(`/aula/${vc.id}`)}
                  >
                    <View style={[styles.imagePlaceholder, { backgroundColor: color.bg }]}>
                      <MaterialCommunityIcons name="play-circle-outline" size={28} color={color.text} />
                    </View>
                    <View style={styles.cardInfo}>
                      <View style={[styles.categoryBadgePurple, { backgroundColor: '#DDF3E8' }]}>
                        <Text style={[styles.badgeTextPurple, { color: '#159B5E' }]}>Vídeo</Text>
                      </View>
                      <Text style={styles.cardCourseTitle} numberOfLines={2}>{vc.titulo}</Text>
                      <Text style={styles.cardCenterName}>{vc.total_aulas ?? 10} aulas</Text>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </>
        )}

        {/* Institutions Quick Access */}
        <TouchableOpacity
          style={styles.institutionCard}
          activeOpacity={0.7}
          onPress={() => router.push('/escolas')}
        >
          <View style={styles.institutionIcon}>
            <MaterialCommunityIcons name="domain" size={24} color="#5B18E6" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.institutionTitle}>Instituições de Formação</Text>
            <Text style={styles.institutionSub}>{schools.length} centros parceiros</Text>
          </View>
          <MaterialCommunityIcons name="chevron-right" size={20} color="#8B8598" />
        </TouchableOpacity>

        {/* Parceiros Externos Section */}
        {partnerList.length > 0 && (
          <>
            <View style={styles.sectionTitleRow}>
              <Text style={styles.sectionTitle}>Centros Parceiros</Text>
              <TouchableOpacity onPress={() => router.push('/centros-parceiros')}>
                <Text style={styles.seeAllText}>Ver todos</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.recommendedContainer}
            >
              {partnerList.slice(0, 5).map((partner, index) => {
                const color = badgeColors[(index + 4) % badgeColors.length];
                const abbr = (partner.nome_empresa || '').substring(0, 2).toUpperCase();
                return (
                  <TouchableOpacity
                    key={partner.id}
                    style={styles.partnerCard}
                    activeOpacity={0.7}
                    onPress={() => {
                      if (partner.centro) {
                        router.push(`/escola/${partner.centro}`);
                      }
                    }}
                  >
                    <View style={[styles.partnerAvatar, { backgroundColor: color.bg }]}>
                      <Text style={[styles.partnerAvatarText, { color: color.text }]}>{abbr}</Text>
                    </View>
                    <Text style={styles.partnerName} numberOfLines={1}>{partner.nome_empresa}</Text>
                    <Text style={styles.partnerType} numberOfLines={1}>{partner.tipo_parceria}</Text>
                    <View style={[styles.partnerBadge, styles.partnerBadgeActive]}>
                      <Text style={[styles.partnerBadgeText, { color: '#159B5E' }]}>
                        Visitar Centro
                      </Text>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </>
        )}

        {/* Popular Courses Section */}
        {popularCourses.length > 6 && (
          <>
            <View style={styles.sectionTitleRow}>
              <Text style={styles.sectionTitle}>Mais Populares</Text>
              <TouchableOpacity onPress={() => router.push('/(tabs)/cursos')}>
                <Text style={styles.seeAllText}>Ver todos</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.recommendedContainer}
            >
              {popularCourses.slice(6, 12).map((course, index) => {
                const color = badgeColors[(index + 3) % badgeColors.length];
                return (
                  <TouchableOpacity
                    key={course.id}
                    style={styles.courseCard}
                    activeOpacity={0.7}
                    onPress={() => router.push(`/curso/${course.id}`)}
                  >
                    <View style={[styles.imagePlaceholder, { backgroundColor: color.bg }]}>
                      <MaterialCommunityIcons name="fire" size={24} color={color.text} />
                    </View>
                    <View style={styles.cardInfo}>
                      <View style={[styles.categoryBadgePurple, { backgroundColor: color.bg }]}>
                        <Text style={[styles.badgeTextPurple, { color: color.text }]}>{course.categoria_nome ?? 'Curso'}</Text>
                      </View>
                      <Text style={styles.cardCourseTitle} numberOfLines={2}>{course.titulo}</Text>
                      <Text style={styles.cardCenterName}>{course.centro_nome ?? ''}</Text>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </>
        )}
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
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    gap: 12,
  },
  avatarContainer: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: '#5B18E6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff',
  },
  welcomeContainer: {
    flex: 1,
  },
  welcomeLabel: {
    fontFamily: 'System',
    fontSize: 12,
    color: '#8B8598',
    fontWeight: '500',
  },
  studentName: {
    fontFamily: 'System',
    fontSize: 17,
    fontWeight: '800',
    color: '#1B1630',
  },
  notificationButton: {
    width: 44,
    height: 44,
    borderRadius: 13,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  notificationDot: {
    position: 'absolute',
    top: 10,
    right: 11,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E8433D',
    borderWidth: 2,
    borderColor: '#ffffff',
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    borderRadius: 16,
    marginHorizontal: 20,
    paddingHorizontal: 16,
    paddingVertical: 13,
    gap: 10,
  },
  searchPlaceholder: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    color: '#9A93AD',
  },
  categoriesContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    gap: 9,
  },
  categoryPill: {
    paddingHorizontal: 15,
    paddingVertical: 9,
    borderRadius: 99,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
  },
  categoryPillActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  categoryText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5A5567',
  },
  categoryTextActive: {
    color: '#ffffff',
  },
  continueCard: {
    marginHorizontal: 20,
    backgroundColor: '#4711C4',
    borderRadius: 22,
    padding: 18,
    position: 'relative',
    overflow: 'hidden',
    shadowColor: '#4711C4',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.5,
    shadowRadius: 30,
    elevation: 8,
  },
  continueTag: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
    color: '#ffffff',
    opacity: 0.85,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  courseTitle: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff',
    marginTop: 7,
    marginBottom: 3,
    maxWidth: 210,
  },
  lessonSub: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.85)',
  },
  progressBarBg: {
    height: 7,
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
    borderRadius: 99,
    marginTop: 14,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 99,
  },
  playButton: {
    position: 'absolute',
    top: 18,
    right: 18,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.18)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginHorizontal: 20,
    marginTop: 22,
    marginBottom: 12,
  },
  sectionTitle: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '800',
    color: '#1B1630',
  },
  seeAllText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
  },
  recommendedContainer: {
    paddingHorizontal: 20,
    gap: 14,
  },
  courseCard: {
    width: 180,
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    overflow: 'hidden',
  },
  imagePlaceholder: {
    height: 96,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardInfo: {
    padding: 11,
    paddingBottom: 14,
  },
  categoryBadgePurple: {
    alignSelf: 'flex-start',
    backgroundColor: '#EDE7FE',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeTextPurple: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
    color: '#5B18E6',
  },
  categoryBadgeGreen: {
    alignSelf: 'flex-start',
    backgroundColor: '#DDF3E8',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeTextGreen: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
    color: '#159B5E',
  },
  cardCourseTitle: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '800',
    color: '#1B1630',
    marginVertical: 8,
    lineHeight: 16,
  },
  cardCenterName: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
  },
  institutionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    marginHorizontal: 20,
    marginTop: 18,
    marginBottom: 24,
    padding: 14,
    gap: 14,
  },
  institutionIcon: {
    width: 46,
    height: 46,
    borderRadius: 14,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  institutionTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '700',
    color: '#1B1630',
  },
  institutionSub: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: "500",
    color: '#8B8598',
    marginTop: 2,
  },
  partnerCard: {
    width: 160,
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 14,
    alignItems: 'center',
  },
  partnerAvatar: {
    width: 52,
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  partnerAvatarText: {
    fontFamily: 'System',
    fontSize: 18,
    fontWeight: '800',
  },
  partnerName: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '700',
    color: '#1B1630',
    textAlign: 'center',
  },
  partnerType: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 2,
    textAlign: 'center',
  },
  partnerBadge: {
    marginTop: 10,
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 8,
    backgroundColor: '#F3F0FB',
  },
  partnerBadgeActive: {
    backgroundColor: '#DDF3E8',
  },
  partnerBadgeText: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '700',
    color: '#8B8598',
  },
});
