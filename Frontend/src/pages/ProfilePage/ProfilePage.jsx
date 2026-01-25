import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useRooms } from '../../context/RoomsContext';
import { useAuth } from '../../context/AuthContext';
import { useProducts } from '../../context/ProductsContext';
import RoomForm from '../../components/RoomForm/RoomForm';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { rooms, addRoom, updateRoom, deleteRoom } = useRooms();
  const { user } = useAuth();
  const { products } = useProducts();
  const [showForm, setShowForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState(null);

  // Calculate user stats
  const userStats = {
    roomCount: rooms.length,
    totalItems: rooms.reduce((sum, r) => sum + (r.products?.length || 0), 0),
    totalValue: rooms.reduce((sum, r) => {
      const roomProducts = products.filter(p => r.products?.includes(p.id));
      return sum + roomProducts.reduce((pSum, p) => pSum + p.price, 0);
    }, 0)
  };

  // Generate room summary
  const getRoomSummary = (room) => {
    const itemCount = room.products?.length || 0;
    const styles = room.styles?.join(' & ') || room.style || 'your';
    
    if (itemCount === 0) return 'Start curating your perfect space';
    return `A ${styles.toLowerCase()} space with ${itemCount} curated item${itemCount > 1 ? 's' : ''}`;
  };

  // Get room icon based on type
  const getRoomIcon = (type) => {
    const icons = {
      'Living Room': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M20 9V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v2" />
          <path d="M2 11v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6a2 2 0 0 0-4 0v2H6v-2a2 2 0 0 0-4 0z" />
          <path d="M4 19v2M20 19v2" />
        </svg>
      ),
      'Bedroom': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M2 4v16M22 4v16M2 8h20M2 16h20" />
          <path d="M6 8v8M18 8v8" />
        </svg>
      ),
      'Office': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2" y="6" width="20" height="12" rx="2" />
          <path d="M12 18v4M8 22h8" />
          <path d="M6 10h.01M10 10h.01" />
        </svg>
      ),
      'Dining Room': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2v8M4.93 10.93l1.41 1.41M2 18h2M20 18h2M19.07 10.93l-1.41 1.41" />
          <path d="M6 18a6 6 0 0 1 12 0" />
          <path d="M12 18v4" />
        </svg>
      ),
    };
    return icons[type] || icons['Living Room'];
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const handleAddRoom = () => {
    setEditingRoom(null);
    setShowForm(true);
  };

  const handleEditRoom = (room) => {
    setEditingRoom(room);
    setShowForm(true);
  };

  const handleDeleteRoom = (roomId) => {
    if (window.confirm('Are you sure you want to delete this room?')) {
      deleteRoom(roomId);
    }
  };

  const handleFormSubmit = (roomData) => {
    if (editingRoom) {
      updateRoom(editingRoom.id, roomData);
    } else {
      addRoom(roomData);
    }
    setShowForm(false);
    setEditingRoom(null);
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingRoom(null);
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Premium Profile Header with Integrated Stats */}
        <motion.div 
          className={styles.profileHeader}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className={styles.headerMain}>
            <div className={styles.userInfo}>
              <div className={styles.userAvatar}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
              <div className={styles.userDetails}>
                <h1 className={styles.userName}>{user?.name || 'Welcome'}</h1>
                <p className={styles.userEmail}>{user?.email || 'guest@furniverse.com'}</p>
                <div className={styles.memberSince}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                  <span>Member since {formatDate(user?.createdAt) || 'Jan 2026'}</span>
                </div>
              </div>
            </div>
            
            {rooms.length > 0 && (
              <div className={styles.statsInline}>
                <div className={styles.statInline}>
                  <span className={styles.statNumber}>{userStats.roomCount}</span>
                  <span className={styles.statText}>{userStats.roomCount === 1 ? 'Room' : 'Rooms'}</span>
                </div>
                <div className={styles.statDivider} />
                <div className={styles.statInline}>
                  <span className={styles.statNumber}>{userStats.totalItems}</span>
                  <span className={styles.statText}>Items</span>
                </div>
                <div className={styles.statDivider} />
                <div className={styles.statInline}>
                  <span className={styles.statNumber}>${userStats.totalValue.toLocaleString()}</span>
                  <span className={styles.statText}>Value</span>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Intro Section */}
        {rooms.length === 0 && (
          <motion.div 
            className={styles.intro}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <div className={styles.introVisual}>
              <div className={styles.introIconWrapper}>
                <div className={styles.introIcon}>🏠</div>
                <div className={styles.introGlow}></div>
              </div>
              <div className={styles.introDots}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <h2 className={styles.introTitle}>Design Your Dream Space</h2>
            <p className={styles.introText}>
              Create personalized room profiles to receive curated furniture recommendations
              tailored to your unique style, budget, and space requirements.
            </p>
            <div className={styles.introFeatures}>
              <div className={styles.feature}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <path d="M22 4L12 14.01l-3-3" />
                </svg>
                <span>Personalized recommendations</span>
              </div>
              <div className={styles.feature}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <path d="M22 4L12 14.01l-3-3" />
                </svg>
                <span>Budget-aware suggestions</span>
              </div>
              <div className={styles.feature}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <path d="M22 4L12 14.01l-3-3" />
                </svg>
                <span>Style-matched furniture</span>
              </div>
            </div>
            <button className={styles.introCTA} onClick={handleAddRoom}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 8v8M8 12h8" />
              </svg>
              Create Your First Room
            </button>
          </motion.div>
        )}

        {/* Rooms Section - Premium Grid Layout */}
        {rooms.length > 0 && (
          <>
            <motion.div 
              className={styles.sectionHeader}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div>
                <h2 className={styles.sectionTitle}>My Spaces</h2>
                <p className={styles.sectionSubtitle}>Click to explore and curate each room</p>
              </div>
              <button className={styles.addButton} onClick={handleAddRoom}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 8v8M8 12h8" />
                </svg>
                New Room
              </button>
            </motion.div>
            
            <div className={styles.roomsGrid}>
              {rooms.map((room, index) => (
                <motion.div 
                  key={room.id} 
                  className={styles.roomCard}
                  onClick={() => navigate(`/room/${room.id}`)}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + index * 0.08, duration: 0.6 }}
                >
                  <div className={styles.roomCardInner}>
                    <div className={styles.roomVisual}>
                      <div className={styles.roomIconBg}>
                        {getRoomIcon(room.roomType)}
                      </div>
                      <div className={styles.roomOverlay}>
                        <div className={styles.roomActions}>
                          <button
                            className={styles.actionBtn}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditRoom(room);
                            }}
                            aria-label="Edit room"
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                          </button>
                          <button
                            className={`${styles.actionBtn} ${styles.delete}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteRoom(room.id);
                            }}
                            aria-label="Delete room"
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M3 6h18" />
                              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className={styles.roomInfo}>
                      <h3 className={styles.roomName}>{room.name}</h3>
                      <p className={styles.roomDesc}>{getRoomSummary(room)}</p>

                      {room.styles && room.styles.length > 0 && (
                        <div className={styles.roomStyles}>
                          {room.styles.slice(0, 2).map((style, idx) => (
                            <span key={idx} className={styles.styleTag}>{style}</span>
                          ))}
                          {room.styles.length > 2 && (
                            <span className={styles.styleMore}>+{room.styles.length - 2}</span>
                          )}
                        </div>
                      )}

                      <div className={styles.roomStats}>
                        <div className={styles.roomStat}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                          </svg>
                          <span>{room.products?.length || 0} items</span>
                        </div>
                        <div className={styles.roomStat}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                          </svg>
                          <span>${(() => {
                            const roomProducts = PRODUCTS.filter(p => room.products?.includes(p.id));
                            return roomProducts.reduce((sum, p) => sum + p.price, 0).toLocaleString();
                          })()}</span>
                        </div>
                        <div className={styles.roomStat}>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                          </svg>
                          <span>Budget ${room.budgetMax?.toLocaleString() || '0'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}

        {/* Premium CTA Section */}
        {rooms.length > 0 && (
          <motion.div 
            className={styles.ctaSection}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            <div className={styles.ctaContent}>
              <div className={styles.ctaIcon}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                  <line x1="12" y1="22.08" x2="12" y2="12" />
                </svg>
              </div>
              <h3 className={styles.ctaTitle}>Ready to bring your vision to life?</h3>
              <p className={styles.ctaText}>
                Explore our curated collection and discover furniture perfectly matched to your style and spaces
              </p>
              <button className={styles.ctaButton} onClick={() => navigate('/shop')}>
                <span>Explore Collection</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Room Form Modal */}
      {showForm && (
        <div className={styles.modal} onClick={handleFormCancel}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <RoomForm
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
              initialData={editingRoom}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
