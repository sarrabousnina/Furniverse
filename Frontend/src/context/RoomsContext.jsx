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
      products: [], // Array to store assigned product IDs
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

  const getRoomById = (roomId) => {
    return rooms.find(room => room.id === roomId) || null;
  };

  const addProductToRoom = (roomId, productId) => {
    setRooms(prev =>
      prev.map(room => {
        if (room.id === roomId) {
          if (room.products && room.products.includes(productId)) {
            return room;
          }
          return {
            ...room,
            products: [...(room.products || []), productId]
          };
        }
        return room;
      })
    );
  };

  const removeProductFromRoom = (roomId, productId) => {
    setRooms(prev =>
      prev.map(room => {
        if (room.id === roomId) {
          return {
            ...room,
            products: (room.products || []).filter(id => id !== productId)
          };
        }
        return room;
      })
    );
  };

  const isProductInRoom = (roomId, productId) => {
    const room = rooms.find(r => r.id === roomId);
    return room?.products?.includes(productId) || false;
  };

  return (
    <RoomsContext.Provider
      value={{
        rooms,
        addRoom,
        updateRoom,
        deleteRoom,
        getActiveRoom,
        getRoomById,
        addProductToRoom,
        removeProductFromRoom,
        isProductInRoom,
      }}
    >
      {children}
    </RoomsContext.Provider>
  );
};
