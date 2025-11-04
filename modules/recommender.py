class Recommender:
    # Exemple simulé de base de données
    sites = [
          {
            id: 1,
            'name': "Hassan Tower",
            'location': "Rabat",
            'description': "The Hassan Tower is a minaret of an incomplete mosque in Rabat. The tower was intended to be the largest minaret in the world along with the mosque, which was also planned to be the world's largest.",
            'image': "pictures/sites/Tour_Hassan.jpeg",
            'rating': 4.7,
            'categories': ["Historical", "Cultural"],
            'duration': "2-3 hours",
            'price': 0, # Free
            'audio': "data/audio/hassan_tower.mp3",
          },
          {
            id: 2,
            'name': "Jemaa el-Fnaa",
            'location': "Marrakech",
            'description': "Jemaa el-Fnaa is a famous square and market place in Marrakech's medina quarter. The square is part of the UNESCO World Heritage site and is best known for its lively atmosphere with local merchants, performers, and food stalls.",
            'image': "pictures/sites/Jemaa_el-Fnaa.jpeg",
            'rating': 4.9,
            'categories': ["Cultural", "Shopping", "Food"],
            'duration': "Half day",
            'price': 0, # Free
            'audio': "data/audio/jemaa_el_fena.mp3",
          },
          {
            id: 3,
            'name': "Chefchaouen Blue City",
            'location': "Chefchaouen",
            'description': "Chefchaouen is a city in northwestern Morocco known for its blue-painted buildings. It's a popular tourist destination with its picturesque medina, historic kasbah, and mountain views.",
            'image': "pictures/sites/Chefchaouen.jpeg",
            'rating': 4.8,
            'categories': ["Photography", "Cultural", "Shopping"],
            'duration': "1-2 days",
            'price': 0, # Free
            'audio': "data/audio/chefchaoun.mp3",
          },
          {
            id: 4,
            'name': "Sahara Desert Tours",
            'location': "Merzouga",
            'description': "Experience the magnificent Sahara Desert through camel trekking and overnight stays in traditional Berber camps under the stars. Watch the sunset over the golden dunes for an unforgettable experience.",
            'image': "pictures/sites/Sahara_Desert.jpeg",
            'rating': 4.9,
            'categories': ["Adventure", "Nature", "Cultural"],
            'duration': "2-3 days",
            'price': 100, # Average price
            'audio': "data/audio/sahara_desert.mp3",
          },
          {
            id: 5,
            'name': "Fes El Bali Medina",
            'location': "Fes",
            'description': "The Fes El Bali Medina is one of the world's largest urban pedestrian zones. This UNESCO World Heritage site is known for its ancient winding architecture, souks, and tanneries.",
            'image': "pictures/sites/Madina_Fes.jpeg",
            'rating': 4.6,
            'categories': ["Historical", "Cultural", "Shopping"],
            'duration': "Full day",
            'price': 0, # Free
            'audio': "data/audio/fes_medina.mp3",
          },
          {
            id: 6,
            'name': "Ouzoud Waterfalls",
            'location': "Azilal Province",
            'description': "The Ouzoud Waterfalls are located near the Middle Atlas village of Tanaghmeilt in the province of Azilal. These 110m high waterfalls are surrounded by lush greenery and often feature rainbows in their mist.",
            'image': "pictures/sites/Ouzoud_Waterfalls.jpeg",
            'rating': 4.5,
            'categories': ["Nature", "Photography", "Adventure"],
            'duration': "Day trip",
            'price': 20, # Average price for guided tours
            'audio': "data/audio/ouzoud_waterfalls.mp3",
          },
        ]

    @staticmethod
    def get_recommendations(preferences):
        recommendations = []
        for site in Recommender.sites:
            if any(pref in site['categories'] for pref in preferences):
                recommendations.append(site)
        return recommendations if recommendations else "Aucune recommandation trouvée."
      
    def get_sites():
      return Recommender.sites