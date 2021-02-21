import { Component } from '@angular/core';
import { NbMenuItem } from '@nebular/theme';

import { faInstagram } from '@fortawesome/free-brands-svg-icons';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  faInstagram = faInstagram;
  title = 'InstaSaver';
  menuItems: NbMenuItem[] = [
    {title: "Archive", icon: "archive", link: "/archive"},
    {title: "Posts", icon: "grid", link: "/posts"},
    {title: "Profiles", icon: "person", link: "/profiles"},
  ]
}
