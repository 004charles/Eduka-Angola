with open("gestoreduka/templates/gestor_base.html", "r") as f:
    content = f.read()

target = """       <!-- User -->
       <div data-kt-dropdown="true" data-kt-dropdown-offset="10px, 10px" data-kt-dropdown-offset-rtl="-20px, 10px" data-kt-dropdown-placement="bottom-start" data-kt-dropdown-placement-rtl="bottom-end" data-kt-dropdown-trigger="click">
        <div class="cursor-pointer shrink-0" data-kt-dropdown-toggle="true">
         <img alt="" class="size-9 rounded-full shrink-0" src="{% static 'metronic/assets/media/avatars/300-2.png' %}"/>
        </div>
        <div class="kt-dropdown-menu w-[250px]" data-kt-dropdown-menu="true">
         <div class="flex items-center justify-between px-2.5 py-1.5 gap-1.5">
          <div class="flex items-center gap-2">
           <img alt="" class="size-9 shrink-0 rounded-full border-2 border-green-500" src="{% static 'metronic/assets/media/avatars/300-2.png' %}"/>
           <div class="flex flex-col">
            <span class="text-sm text-foreground font-semibold leading-none">
             {{ request.user.nome }}
            </span>
            <a class="text-xs text-secondary-foreground hover:text-primary font-medium leading-none" href="{% url 'configuracao_gestor' %}">
             {{ request.user.email }}
            </a>
           </div>
          </div>
          <span class="kt-badge kt-badge-sm kt-badge-primary kt-badge-outline">
           Pro
          </span>
         </div>
         <ul class="kt-dropdown-menu-sub">
          <li>
           <div class="kt-dropdown-menu-separator">
           </div>
          </li>
          <li>
           <a class="kt-dropdown-menu-link" href="{% url 'perfil_institucional_interno' %}">
            <i class="ki-filled ki-badge">
            </i>
            Public Profile
           </a>
          </li>
          <li>
           <a class="kt-dropdown-menu-link" href="{% url 'configuracao_gestor' %}">
            <i class="ki-filled ki-profile-circle">
            </i>
            Meu Perfil
           </a>
          </li>
          <li data-kt-dropdown="true" data-kt-dropdown-placement="right-start" data-kt-dropdown-trigger="hover">
           <button class="kt-dropdown-menu-toggle" data-kt-dropdown-toggle="true">
            <i class="ki-filled ki-setting-2">
            </i>
            Minha Conta
            <span class="kt-dropdown-menu-indicator">
             <i class="ki-filled ki-right text-xs">
             </i>
            </span>
           </button>
           <div class="kt-dropdown-menu w-[220px]" data-kt-dropdown-menu="true">
            <ul class="kt-dropdown-menu-sub">
             <li>
              <a class="kt-dropdown-menu-link" href="{% url 'configuracao_gestor' %}">
               <i class="ki-filled ki-coffee">
               </i>
               Definições
              </a>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="{% url 'configuracao_gestor' %}">
               <i class="ki-filled ki-some-files">
               </i>
               Meu Perfil
              </a>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="index.html#">
               <span class="flex items-center gap-2">
                <i class="ki-filled ki-icon">
                </i>
                Billing
               </span>
               <span class="ms-auto inline-flex items-center" data-kt-tooltip="true" data-kt-tooltip-placement="top">
                <i class="ki-filled ki-information-2 text-base text-muted-foreground">
                </i>
                <span class="kt-tooltip" data-kt-tooltip-content="true">
                 Payment and subscription info
                </span>
               </span>
              </a>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="account/security/overview.html">
               <i class="ki-filled ki-medal-star">
               </i>
               Security
              </a>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="account/members/teams.html">
               <i class="ki-filled ki-setting">
               </i>
               Members &amp; Roles
              </a>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="account/integrations.html">
               <i class="ki-filled ki-switch">
               </i>
               Integrations
              </a>
             </li>
             <li>
              <div class="kt-dropdown-menu-separator">
              </div>
             </li>
             <li>
              <a class="kt-dropdown-menu-link" href="account/security/overview.html">
               <span class="flex items-center gap-2">
                <i class="ki-filled ki-shield-tick">
                </i>
                Notificações
               </span>
               <input checked="" class="ms-auto kt-switch" name="check" type="checkbox" value="1"/>
              </a>
             </li>
            </ul>
           </div>
          </li>
          <li>
           <a class="kt-dropdown-menu-link" href="../../../../devs.keenthemes.com/index.html">
            <i class="ki-filled ki-message-programming">
            </i>
            Dev Forum
           </a>
          </li>
          <li data-kt-dropdown="true" data-kt-dropdown-placement="right-start" data-kt-dropdown-trigger="hover">
           <button class="kt-dropdown-menu-toggle py-1" data-kt-dropdown-toggle="true">
            <span class="flex items-center gap-2">
             <i class="ki-filled ki-icon">
             </i>
             Language
            </span>
            <span class="ms-auto kt-badge kt-badge-stroke shrink-0">
             English
             <img alt="" class="inline-block size-3.5 rounded-full" src="{% static 'metronic/assets/media/flags/united-states.svg' %}"/>
            </span>
           </button>
           <div class="kt-dropdown-menu w-[180px]" data-kt-dropdown-menu="true">
            <ul class="kt-dropdown-menu-sub">
             <li class="active">
              <a class="kt-dropdown-menu-link" href="index.html%3Fdir=ltr.html">
               <span class="flex items-center gap-2">
                <img alt="" class="inline-block size-4 rounded-full" src="{% static 'metronic/assets/media/flags/united-states.svg' %}"/>
                <span class="kt-menu-title">
                 English
                </span>
               </span>
               <i class="ki-solid ki-check-circle ms-auto text-green-500 text-base">
               </i>
              </a>
             </li>
             <li class="">
              <a class="kt-dropdown-menu-link" href="index.html%3Fdir=rtl.html">
               <span class="flex items-center gap-2">
                <img alt="" class="inline-block size-4 rounded-full" src="{% static 'metronic/assets/media/flags/saudi-arabia.svg' %}"/>
                <span class="kt-menu-title">
                 Arabic(Saudi)
                </span>
               </span>
              </a>
             </li>
             <li class="">
              <a class="kt-dropdown-menu-link" href="index.html%3Fdir=ltr.html">
               <span class="flex items-center gap-2">
                <img alt="" class="inline-block size-4 rounded-full" src="{% static 'metronic/assets/media/flags/spain.svg' %}"/>
                <span class="kt-menu-title">
                 Spanish
                </span>
               </span>
              </a>
             </li>
             <li class="">
              <a class="kt-dropdown-menu-link" href="index.html%3Fdir=ltr.html">
               <span class="flex items-center gap-2">
                <img alt="" class="inline-block size-4 rounded-full" src="{% static 'metronic/assets/media/flags/germany.svg' %}"/>
                <span class="kt-menu-title">
                 German
                </span>
               </span>
              </a>
             </li>
             <li class="">
              <a class="kt-dropdown-menu-link" href="index.html%3Fdir=ltr.html">
               <span class="flex items-center gap-2">
                <img alt="" class="inline-block size-4 rounded-full" src="{% static 'metronic/assets/media/flags/japan.svg' %}"/>
                <span class="kt-menu-title">
                 Japanese
                </span>
               </span>
              </a>
             </li>
            </ul>
           </div>
          </li>
          <li>
           <div class="kt-dropdown-menu-separator">
           </div>
          </li>
         </ul>
         <div class="px-2.5 pt-1.5 mb-2.5 flex flex-col gap-3.5">
          <div class="flex items-center gap-2 justify-between">
           <span class="flex items-center gap-2">
            <i class="ki-filled ki-moon text-base text-muted-foreground">
            </i>
            <span class="font-medium text-2sm">
             Dark Mode
            </span>
           </span>
           <input class="kt-switch" data-kt-theme-switch-state="dark" data-kt-theme-switch-toggle="true" name="check" type="checkbox" value="1"/>
          </div>
          <a class="kt-btn kt-btn-outline justify-center w-full" href="{% url 'logout_gestor' %}">
           Log out
          </a>
         </div>
        </div>
       </div>"""

replacement = """       <!-- User -->
       <div data-kt-dropdown="true" data-kt-dropdown-offset="10px, 10px" data-kt-dropdown-offset-rtl="-20px, 10px" data-kt-dropdown-placement="bottom-start" data-kt-dropdown-placement-rtl="bottom-end" data-kt-dropdown-trigger="click">
        <div class="cursor-pointer shrink-0" data-kt-dropdown-toggle="true">
         {% if centro and centro.perfil.imagem %}
          <img alt="" class="size-9 rounded-full shrink-0 object-cover" src="{{ centro.perfil.imagem.url }}"/>
         {% else %}
          <div class="size-9 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0 border border-primary/20">
           {{ request.user.nome|slice:":1"|upper }}
          </div>
         {% endif %}
        </div>
        <div class="kt-dropdown-menu w-[250px]" data-kt-dropdown-menu="true">
         <div class="flex items-center justify-between px-2.5 py-1.5 gap-1.5">
          <div class="flex items-center gap-2">
           {% if centro and centro.perfil.imagem %}
            <img alt="" class="size-9 rounded-full shrink-0 object-cover border-2 border-green-500" src="{{ centro.perfil.imagem.url }}"/>
           {% else %}
            <div class="size-9 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm shrink-0 border-2 border-green-500">
             {{ request.user.nome|slice:":1"|upper }}
            </div>
           {% endif %}
           <div class="flex flex-col">
            <span class="text-sm text-foreground font-semibold leading-none">
             {{ request.user.nome }}
            </span>
            <a class="text-xs text-secondary-foreground hover:text-primary font-medium leading-none" href="{% url 'configuracao_gestor' %}">
             {{ request.user.email }}
            </a>
           </div>
          </div>
         </div>
         <ul class="kt-dropdown-menu-sub">
          <li>
           <div class="kt-dropdown-menu-separator">
           </div>
          </li>
          <li>
           <a class="kt-dropdown-menu-link" href="{% url 'perfil_institucional_interno' %}">
            <i class="ki-filled ki-badge">
            </i>
            Public Profile
           </a>
          </li>
          <li>
           <a class="kt-dropdown-menu-link" href="{% url 'configuracao_gestor' %}">
            <i class="ki-filled ki-profile-circle">
            </i>
            Meu Perfil
           </a>
          </li>
          <li>
           <div class="kt-dropdown-menu-separator">
           </div>
          </li>
         </ul>
         <div class="px-2.5 pt-1.5 mb-2.5 flex flex-col gap-3.5">
          <div class="flex items-center gap-2 justify-between">
           <span class="flex items-center gap-2">
            <i class="ki-filled ki-moon text-base text-muted-foreground">
            </i>
            <span class="font-medium text-2sm">
             Dark Mode
            </span>
           </span>
           <input class="kt-switch" data-kt-theme-switch-state="dark" data-kt-theme-switch-toggle="true" name="check" type="checkbox" value="1"/>
          </div>
          <a class="kt-btn kt-btn-outline justify-center w-full" href="{% url 'logout_gestor' %}">
           Sair da Conta
          </a>
         </div>
        </div>
       </div>"""

if target in content:
    with open("gestoreduka/templates/gestor_base.html", "w") as f:
        f.write(content.replace(target, replacement))
    print("SUCCESS: Replaced the User dropdown")
else:
    print("FAILED: Could not find the exact target string")
