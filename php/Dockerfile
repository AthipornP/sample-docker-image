FROM php:8.2-apache

# Install composer and required extensions
RUN apt-get update && apt-get install -y unzip git && rm -rf /var/lib/apt/lists/*

# Enable mod_rewrite
RUN a2enmod rewrite

WORKDIR /var/www/html

COPY composer.json composer.lock* /var/www/html/
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
 && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
 && php -r "unlink('composer-setup.php');"

RUN composer install --no-interaction --no-dev --prefer-dist

COPY public/ /var/www/html/

EXPOSE 80
CMD ["apache2-foreground"]
