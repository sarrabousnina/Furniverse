import React, { createContext, useContext, useState, useEffect } from 'react';

const RoomsContext = createContext();

export const useRooms = () => {
  const context = useContext(RoomsContext);
  if (!context) {
    throw new Error('useRooms must be used within a RoomsProvider');
  }
  return context;
};

export const RoomsProvider = ({ children }) => {
  const [rooms, setRooms] = useState(() => {
    const savedRooms = localStorage.getItem('furniverse_rooms');
    return savedRooms ? JSON.parse(savedRooms) : [];
  });

  useEffect(() => {
    localStorage.setItem('furniverse_rooms', JSON.stringify(rooms));
  }, [rooms]);

  const addRoom = (roomData) => {
    const newRoom = {
      ...roomData,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
    };
    setRooms(prev => [...prev, newRoom]);
    return newRoom;
  };

  const updateRoom = (roomId, roomData) => {
    setRooms(prev =>
      prev.map(room =>
        room.id === roomId ? { ...room, ...roomData } : room
      )
    );
  };

  const deleteRoom = (roomId) => {
    setRooms(prev => prev.filter(room => room.id !== roomId));
  };

  const getActiveRoom = () => {
    return rooms.length > 0 ? rooms[0] : null;
  };

  return (
    <RoomsContext.Provider
      value={{
        rooms,
        addRoom,
        updateRoom,
        deleteRoom,
        getActiveRoom,
      }}
    >
      {children}
    </RoomsContext.Provider>
  );
};
