import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRooms } from '../../context/RoomsContext';
import { useAuth } from '../../context/AuthContext';
import RoomForm from '../../components/RoomForm/RoomForm';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { rooms, addRoom, updateRoom, deleteRoom } = useRooms();
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState(null);

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
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>My Profile</h1>
            <p className={styles.subtitle}>
              Welcome back{user ? `, ${user.name}` : ''}! Manage your room profiles and preferences.
            </p>
          </div>
          <button className={styles.addButton} onClick={handleAddRoom}>
            <span>+</span> Add New Room
          </button>
        </div>

        {/* Intro Section */}
        {rooms.length === 0 && (
          <div className={styles.intro}>
            <div className={styles.introIcon}>🏠</div>
            <h2 className={styles.introTitle}>Create Your First Room Profile</h2>
            <p className={styles.introText}>
              Tell us about your space, style preferences, and budget. We'll use this information
              to provide personalized furniture recommendations throughout the store.
            </p>
          </div>
        )}

        {/* Rooms Grid */}
        {rooms.length > 0 && (
          <div className={styles.roomsGrid}>
            {rooms.map(room => (
              <div 
                key={room.id} 
                className={styles.roomCard}
                onClick={() => navigate(`/room/${room.id}`)}
              >
                <div className={styles.roomHeader}>
                  <h3 className={styles.roomTitle}>{room.name}</h3>
                  <div className={styles.roomActions}>
                    <button
                      className={styles.iconButton}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditRoom(room);
                      }}
                      aria-label="Edit room"
                    >
                      <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                    <button
                      className={`${styles.iconButton} ${styles.delete}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteRoom(room.id);
                      }}
                      aria-label="Delete room"
                    >
                      <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
                        <path d="M3 6h18" />
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div className={styles.roomDetails}>
                  {/* Products Count */}
                  <div className={styles.detailRow}>
                    <svg className={styles.detailIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                    </svg>
                    <span className={styles.detailLabel}>Furniture:</span>
                    <span className={`${styles.detailValue} ${styles.productsValue}`}>
                      {room.products?.length || 0} items
                    </span>
                  </div>

                  {/* Budget */}
                  <div className={styles.detailRow}>
                    <svg className={styles.detailIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                    </svg>
                    <span className={styles.detailLabel}>Budget:</span>
                    <span className={`${styles.detailValue} ${styles.budgetValue}`}>
                      ${room.budgetMin?.toLocaleString() || '0'} – ${room.budgetMax?.toLocaleString() || '0'}
                    </span>
                  </div>

                  {/* Size */}
                  {room.size && (
                    <div className={styles.detailRow}>
                      <svg className={styles.detailIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 3h18v18H3z" />
                        <path d="M3 9h18M9 3v18" />
                      </svg>
                      <span className={styles.detailLabel}>Size:</span>
                      <span className={styles.detailValue}>{room.size.toLocaleString()} sq ft</span>
                    </div>
                  )}

                  {/* Styles */}
                  {room.styles && room.styles.length > 0 && (
                    <div className={styles.styles}>
                      {room.styles.map((style, idx) => (
                        <span key={idx} className={styles.styleBadge}>
                          {style}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Existing Furniture */}
                  {room.existingFurniture && (
                    <div className={styles.furniture}>
                      ✨ {room.existingFurniture}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Shop Prompt */}
        {rooms.length > 0 && (
          <div style={{ textAlign: 'center', marginTop: '48px' }}>
            <p style={{ fontSize: '1.125rem', color: '#6B6B6B', marginBottom: '16px' }}>
              Ready to shop with your personalized recommendations?
            </p>
            <button
              className={styles.addButton}
              onClick={() => navigate('/shop')}
            >
              Browse Furniture →
            </button>
          </div>
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
