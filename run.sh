docker build -t wg-image .
docker run --rm -p 5000:5000 -e BASE_DIR='/' wg-image