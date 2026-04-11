const { Jimp } = require('jimp');
const path = require('path');

async function removeBackground() {
    try {
        const imagePath = path.join('c:', 'Users', 'Lenovo', 'Documents', 'kitob', 'book-cover.png');
        const outputPath = path.join('c:', 'Users', 'Lenovo', 'Documents', 'kitob', 'book-cover.png');
        
        const image = await Jimp.read(imagePath);
        
        // Oq rangga yaqin piksellarni shaffof (transparent) qilish
        image.scan(0, 0, image.bitmap.width, image.bitmap.height, function(x, y, idx) {
            const r = this.bitmap.data[idx + 0];
            const g = this.bitmap.data[idx + 1];
            const b = this.bitmap.data[idx + 2];
            
            // Agar piksel oq rangda bo'lsa (R, G, B > 240)
            if (r > 245 && g > 245 && b > 245) {
                this.bitmap.data[idx + 3] = 0; // Alpha kanalini 0 qilish (shaffof)
            }
        });
        
        await image.writeAsync(outputPath);
        console.log('Background removed successfully!');
    } catch (err) {
        console.error('Error processing image:', err);
    }
}

removeBackground();
