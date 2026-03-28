const CONFIG = {
    DISCORD_ID: '',
    WAKATIME_URL: '',
    CITY: 'Tu Ciudad',
    GITHUB_TOPIC: 'portfolio',

    PROJECTS: [
        {
            id: 'proyecto-1',
            title: 'Nombre del Proyecto 1',
            shortDesc: 'Descripción breve del proyecto para mostrar en la tarjeta.',
            longDesc: 'Explica aquí el objetivo del proyecto, cómo lo construiste y qué problema resuelve. Puedes incluir decisiones técnicas, resultados y próximos pasos.',
            tech: ['Tecnologia 1', 'Tecnologia 2', 'Tecnologia 3'],
            image: 'https://via.placeholder.com/600x400/111/00ff00?text=Tu+Proyecto',
            link: 'https://github.com/tu-usuario/tu-repo'
        },
        {
            id: 'proyecto-2',
            title: 'Nombre del Proyecto 2',
            shortDesc: 'Otra descripción corta con foco en impacto o funcionalidad.',
            longDesc: 'Usa este bloque para contar el contexto del proyecto, su arquitectura y los aprendizajes clave. Mantén un tono claro y directo.',
            tech: ['Framework', 'Backend', 'Frontend', 'Cloud'],
            image: 'https://via.placeholder.com/600x400/111/00ff00?text=Proyecto+2',
            link: 'https://github.com/tu-usuario/otro-repo'
        }
    ]
};

/* 
    //Template para agregar proyectos. Solo copia este bloque y rellena los campos para agregar un nuevo proyecto.
    id: 'project-id', // Un ID único para el proyecto (usado para anclar el proyecto en la URL, ej: #project-id)
    title: 'Project Title', // El título del proyecto
    shortDesc: 'Short description of the project.', // Una descripción corta para mostrar en la tarjeta del proyecto
    longDesc: 'A longer description of the project, detailing what it is about, the technologies used, and any other relevant information.', // Una descripción larga para mostrar en la página del proyecto
    tech: ['Tech1', 'Tech2', 'Tech3'], // Una lista de tecnologías usadas en el proyecto para mostrar como etiquetas
    image: 'https://via.placeholder.com/600x400/111/00ff00?text=Project+Image', // Un link a una imagen representativa del proyecto (puede ser un screenshot o logo) (Yo suelo sacar screenshots de los proyectos y subirlos a "https://squoosh.app/editor" para reducir su tamaño sin perder mucha calidad, y luego los subo a la carpeta "img" de mi proyecto para usarlos desde ahí)
    link: '' // Un link al repositorio del proyecto o a una página donde se pueda ver más información (ej: GitHub, demo en vivo, etc.)
*/
