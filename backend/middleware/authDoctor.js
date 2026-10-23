import jwt from 'jsonwebtoken'

// doctor authentication middleware
const authDoctor = async (req, res, next) => {
          try {
                    // we have passed dToken from frontend but here req.headers make it dtoken that why it caught error 
                    const {dtoken} = req.headers
                    
                    if (!dtoken) {
                              return res.json({ success: false, message: 'Not Authorize Login Again' })
                    }

                    const token_decode = jwt.verify(dtoken, process.env.JWT_SECRET)

                    req.docId = token_decode.id

                    next()

          } catch (error) {
                    console.log(error)
                    res.json({ success: false, message: error.message })
          }
}

export default authDoctor