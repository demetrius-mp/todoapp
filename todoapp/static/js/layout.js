function flash(categoria, texto, config) {
    if (categoria === 'success') {
        tata.success('Sucesso', texto, config)
    }

    else if (categoria === 'warn') {
        tata.warn('Info', texto, config)
    }

    else if (categoria === 'info') {
        tata.info('Info', texto, config)
    }

    else if (categoria === 'danger') {
        tata.error('Erro', texto, config)
    }
}