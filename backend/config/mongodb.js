import mongoose from 'mongoose';

const connectDB = async () => {
  // connected event
  mongoose.connection.on('connected', () => console.log("MongoDB connected successfully"))

  mongoose.connection.on('error', (err) => console.log("MongoDB connection error:", err))

  try {
    await mongoose.connect(process.env.MONGODB_URI, { dbName: 'prescripto' })
    console.log("Database created successfully")
  } catch (error) {
    console.log("Failed to connect to MongoDB:", error.message)
  }
}

export default connectDB
